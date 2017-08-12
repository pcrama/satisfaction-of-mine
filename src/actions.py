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
    return requests.get(req.url, params=req.params).text


@attr.s
class ReadJSON:
    filename = attr.ib()


def get_config_json(fname):
    return Effect(ReadJSON(os.path.abspath(fname)))

@sync_performer
def perform_read_json(dispatcher, read_json):
    with open(read_json.filename) as fp:
        return json.load(fp, parse_int=float)


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

def do_print(fmt, *args, **kwargs):
    return Effect(Print(fmt.format(*args, **kwargs)))


IO_DISPATCHER = ComposedDispatcher([
    TypeDispatcher({ReadJSON: perform_read_json,
                    GetCurrentDate: perform_get_current_date,
                    HttpRequest: perform_http_request,
                    Print: perform_print,
    }),
    base_dispatcher])
