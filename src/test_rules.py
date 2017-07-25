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


class TestMatchCategory(unittest.TestCase):
    def test_001_create_MatchCategory(self):
        "MatchCategory validates its target category"
        with self.assertRaisesRegex(TypeError, "category"):
            r = rules.MatchCategory(1234)

    def test_002_create_MatchCategory(self):
        r = rules.MatchCategory("Automation")

    def test_003_use_MatchCategory(self):
        "A matching category in a time entry is recognized"
        category = "12345"
        r = rules.MatchCategory(category)
        e = _make_TimeEntry(category=category)
        self.assertTrue(r.match(e))

    def test_004_use_MatchCategory(self):
        "A mismatching category in a time entry is rejected"
        r = rules.MatchCategory("12345")
        e = _make_TimeEntry(category="6789")
        self.assertFalse(r.match(e))


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
