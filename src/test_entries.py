#!/usr/bin/env python3
import unittest

import entries

class TestTimeEntry(unittest.TestCase):
    def test_001_create_TimeEntry(self):
        "TimeEntry validates its input `issue_id'"
        with self.assertRaisesRegex(TypeError, "issue_id"):
            entries.TimeEntry(12345, 1.0, "Automation")

    def test_002_create_TimeEntry(self):
        "TimeEntry validates its input `duration'"
        param_name = "duration"
        create_with_duration = lambda d: entries.TimeEntry(
            "12345", d, "Automation")
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_duration(None)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_duration(-2.1)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_duration(-1)

    def test_003_create_TimeEntry(self):
        "TimeEntry validates its input `category'"
        param_name = "category"
        create_with_category = lambda c: entries.TimeEntry("12345", 2.0, c)
        with self.assertRaisesRegex(TypeError, param_name):
            create_with_category(None)
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_category("")
        with self.assertRaisesRegex(ValueError, param_name):
            create_with_category(" ")

    def test_100_create_valid_TimeEntry(self):
        entries.TimeEntry("12345", 8.0, "Automation")


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
