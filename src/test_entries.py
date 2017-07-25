#!/usr/bin/env python3
import unittest

import entries

class TestTimeEntry(unittest.TestCase):
    def test_001_create_TimeEntry(self):
        "TimeEntry validates its input `issue_id'"
        param_name = "issue_id"
        create_with_issue_id = lambda i: entries.TimeEntry(
            i, 3.0, "Automation", "", "2017-07-24")
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_issue_id(12345)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_issue_id("")

    def test_002_create_TimeEntry(self):
        "TimeEntry validates its input `duration'"
        param_name = "duration"
        create_with_duration = lambda d: entries.TimeEntry(
            "12345", d, "Automation", "", "2017-07-24")
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_duration(None)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_duration(-2.1)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_duration(-1)

    def test_003_create_TimeEntry(self):
        "TimeEntry validates its input `category'"
        param_name = "category"
        create_with_category = lambda c: entries.TimeEntry(
            "12345", 2.0, c, "comment", "2017-07-24")
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_category(None)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_category("")
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_category(" ")

    def test_004_create_TimeEntry(self):
        "TimeEntry validates its input `comment'"
        with self.assertRaisesRegex(TypeError, "comment"):
            entries.TimeEntry("12345", 1.0, "Automation", 1234, "2017-07-24")

    def test_005_create_TimeEntry(self):
        "TimeEntry validates its input `issue_id'"
        param_name = "issue_id"
        create_with_issue_id = lambda i: entries.TimeEntry(
            i, 3.0, "Automation", "", "2017-07-24")
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_issue_id(12345)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_issue_id("")
        
    def test_006_create_TimeEntry(self):
        "TimeEntry validates its input `date'"
        param_name = "date"
        create_with_date = lambda d: entries.TimeEntry(
            "12345", 1.2, "Automation", "", d)
        # TODO: conversion from string lets parsing assertion error bubble up.
        # I'm checking for that for simplicity now.  The proper thing would be
        # to wrap that exception into an error mentioning the parameter name.
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_date(1234)
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_date("1234")
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_date("1234-56-78")

    def test_100_create_valid_TimeEntry(self):
        entries.TimeEntry("12345", 8.0, "Automation", "comment", "2017-07-24")


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
