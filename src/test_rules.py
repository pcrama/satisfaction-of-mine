#!/usr/bin/env python3
import unittest

import entries
import rules

def _make_TimeEntry(issue_id="12345", duration=1.0, category="Test",
                    comment="", date="2017-07-26"):
    return entries.TimeEntry(issue_id, duration, category, comment, date)


class TestMatchIssueID(unittest.TestCase):
    def test_001_create_MatchIssueID(self):
        "You can create a rule matching a precise issue ID but only using a str"
        with self.assertRaises(TypeError):
            r = rules.MatchIssueID(1234)

    def test_002_create_MatchIssueID(self):
        "You can create a rule matching a precise issue ID"
        r = rules.MatchIssueID("01234")

    def test_003_use_MatchIssueID(self):
        "A matching issue ID in a time entry is recognized"
        issue_id = "12345"
        r = rules.MatchIssueID(issue_id)
        e = _make_TimeEntry(issue_id=issue_id)
        self.assertTrue(r.match(e))

    def test_004_use_MatchIssueID(self):
        "A mismatching issue ID in a time entry is rejected"
        r = rules.MatchIssueID("12345")
        e = _make_TimeEntry(issue_id="6789")
        self.assertFalse(r.match(e))


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
