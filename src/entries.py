"Time entries are represented by the L{TimeEntry} class"

import csv
import datetime
import re
from typing import Iterator

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


_EXTRACT_ISSUE_ID = re.compile("[^#]* #([0-9]+): .*")
"@var: Extract issue number from Redmine `issue' column"

def parse_from(s: str) -> Iterator[TimeEntry]:
    lines = csv.reader(x for x in s.split("\n"))
    header = next(lin for lin in lines if lin)  # skip leading empty lines
    # Looking for the column indexes with header.index will raise ValueError
    # if the column isn't found
    issue_idx = header.index("Issue")
    duration_idx = header.index("Hours")
    category_idx = header.index("Activity")
    comment_idx = header.index("Comment")
    date_idx = header.index("Date")
    for row in lines:
        if len(row) < len(header):
            continue  # ignore incomplete lines
        issue = _EXTRACT_ISSUE_ID.match(row[issue_idx]).group(1)
        yield TimeEntry(issue,
                        float(row[duration_idx]),
                        row[category_idx],
                        row[comment_idx],
                        row[date_idx],
        )
