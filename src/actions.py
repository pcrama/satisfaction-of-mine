"Side-effecting actions"

import datetime
import json
import os

import attr
from effect import (
    ComposedDispatcher,
    Effect,
    TypeDispatcher,
    base_dispatcher,
    sync_perform,
    sync_performer,
)
from effect.do import (
    do,
    do_return
)
from effect.testing import perform_sequence
import requests

@attr.s
class HttpRequest:
    url = attr.ib(validator=attr.validators.instance_of(str))
    params = attr.ib(validator=attr.validators.instance_of(dict),
                     default=attr.Factory(dict))

def get_redmine_info(
        base_url: str,
        user: str,
        start_date: datetime.date,
        end_date: datetime.date,
        api_key: str,
) -> Effect:
    return Effect(HttpRequest(
        base_url,
        {"c[]": ["project", "spent_on", "user", "activity", "issue",
                 "comments", "hours",],
         "f[]": ["user_id","spent_on", ""],
         "op[spent_on]": "><",
         "op[user_id]": "=",
         "v[spent_on][]": ["{:%Y-%m-%d}".format(x) for x in (
             start_date, end_date)],
         "v[user_id][]": user,
         "key": api_key,
        }))


@sync_performer
def perform_http_request(dispatcher, req):
    return requests.get(req.url, params=req.params)


@attr.s
class ReadJSON:
    filename = attr.ib()


def get_config_json(fname):
    return Effect(ReadJSON(os.path.abspath(fname)))

@sync_performer
def perform_read_json(dispatcher, read_json):
    with open(read_json.filename) as fp:
        return json.load(fp)


class GetCurrentDate:
    pass


def get_current_date():
    return Effect(GetCurrentDate())

@sync_performer
def perform_get_current_date(_dispatcher, _gcd):
    return datetime.date.today()


@attr.s
class Print:
    text = attr.ib()

@sync_performer
def perform_print(dispatcher, p):
    print(p.text)


IO_DISPATCHER = ComposedDispatcher([
    TypeDispatcher({ReadJSON: perform_read_json,
                    GetCurrentDate: perform_get_current_date,
                    HttpRequest: perform_http_request,
    }),
    base_dispatcher])

@attr.s
class ReadLine:
    prompt = attr.ib()


def get_user_name():
    return Effect(ReadLine("Enter User Name> "))

@do
def get_user_age(name):
    try:
        age = yield Effect(ReadLine("{}, what is your age? ".format(name)))
    except Exception as e:
        yield do_print("There was a problem getting your age: {}".format(e))
    else:
        yield do_return(int(age))

def do_print(fmt, *args, **kwargs):
    return Effect(Print(fmt.format(*args, **kwargs)))

@do
def age():
    try:
        name = yield get_user_name()
    except Exception as e:
        yield do_print("There was a problem: {}".format(e))
    else:
        emphasize = False
        while True: # loop will be exited by explicit return
            try:
                age = yield get_user_age(name.upper() if emphasize else name)
            except Exception as e:
                yield do_print("{}, you should have entered your age correctly: {}".
                               format(name, e))
            else:
                if age < 18:
                    emphasize = True
                    yield do_print("{} is too young", age)
                else:
                    return (name, age)

@sync_performer
def perform_readline(dispatcher, readline):
    return input(readline.prompt)

def main():
    eff = age()
    return sync_perform(ComposedDispatcher([TypeDispatcher({ReadLine: perform_readline,
                                                            Print: perform_print}),
                                            base_dispatcher]),
                        eff)

def test1_main():
    resp = "Philippe"
    print_and_return = lambda k, ret: (lambda i: (print("{}: {}".format(k, i)) or ret))
    seq = [(ReadLine("Enter User Name> "), print_and_return(1, resp)),
           (ReadLine("{}, what is your age? ".format(resp)), print_and_return(2, 19))]
    eff = age()
    return (resp, 19) == perform_sequence(seq, eff)

def test2_main():
    resp = "Philippe"
    ages = [3, 4, 5, 6, 7, 8, 19]
    print_and_return = lambda k, ret: (lambda i: (print("{}: {}".format(k, i)) or ret))
    seq = [(ReadLine("Enter User Name> "), print_and_return(1, resp))]
    for idx, h in enumerate(ages):
        seq.append((ReadLine("{}, what is your age? ".format(resp if idx == 0 else resp.upper())),
                    print_and_return(idx + 2, h)))
        if h < 18:
            seq.append((Print("{} is too young".format(h)), print_and_return(idx + 2.5, None)))
    eff = age()
    return perform_sequence(seq, eff)

def test3_main():
    resp = "Philippe"
    ages = [3, "abc", 19]
    print_and_return = lambda k, ret: (lambda i: (print("{}: {}".format(k, i)) or ret))
    seq = [(ReadLine("Enter User Name> "), print_and_return(1, resp))]
    for idx, h in enumerate(ages):
        seq.append((ReadLine("{}, what is your age? ".format(resp if idx == 0 else resp.upper())),
                    print_and_return(idx + 2, h)))
        if not isinstance(h, int):
            seq.append((Print("{}, you should have entered your age correctly: invalid literal for int() with base 10: {!r}".
                              format(resp, h)),
                        print_and_return(idx + 2.5, None)))
        elif h < 18:
            seq.append((Print("{} is too young".format(h)), print_and_return(idx + 2.5, None)))
    eff = age()
    return perform_sequence(seq, eff)
