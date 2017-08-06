"Time entries are represented by the L{TimeEntry} class"

import csv
import datetime

import attr

def _convert_date(x):
    try:
        return datetime.datetime.strptime(x, "%Y-%m-%d").date()
    except Exception:
        return x

@attr.s
class TimeEntry(object):
    def _validate_string_and_not_blank(self, attribute, value):
        attr.validators.instance_of(str)(self, attribute, value)
        if len(value.strip()) == 0:
            raise ValueError("'{name}' must be non-blank and {value!r} isn't".
                             format(name=attribute.name, value=value))
    issue_id = attr.ib(validator=_validate_string_and_not_blank)
    duration = attr.ib()
    @duration.validator
    def _validate_duration(self, attribute, value):
        attr.validators.instance_of((int, float))(self, attribute, value)
        if value < 0:
            raise ValueError("'{name}' must be >= 0 and {value!r} isn't".format(
                name=attribute.name, value=value))
    category = attr.ib(validator=_validate_string_and_not_blank)
    comment = attr.ib(validator=attr.validators.instance_of(str))
    date = attr.ib(convert=_convert_date,
                   validator=attr.validators.instance_of(datetime.date))


def parse_from(s):
    lines = csv.reader(x for x in s.split("\n"))
    header = next(lines)
    issue_idx = header.index("Issue")
    duration_idx = header.index("Hours")
    category_idx = header.index("Activity")
    comment_idx = header.index("Comment")
    date_idx = header.index("Date")
    for row in lines:
        yield TimeEntry(row[issue_idx],
                        float(row[duration_idx]),
                        row[category_idx],
                        row[comment_idx],
                        "2017-08-01",
                        ) #row[date_idx])
