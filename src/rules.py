"""Interpret rules to compute satisfaction score of a given time entry"""

import attr

import entries

@attr.s
class MatchIssueID(object):
    issue_id = attr.ib(validator=attr.validators.instance_of(str)) # type: str

    def match(self, e: entries.TimeEntry) -> bool:
        return e.issue_id == self.issue_id
