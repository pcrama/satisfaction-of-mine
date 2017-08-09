import io
import sys
import unittest

from typing import Any

import main

class TestArgParse(unittest.TestCase):
    def setUp(self):
        self.arg_parser = main.make_command_line_parser()
        # Capture output to validate
        self.backup_out = sys.stdout
        self.backup_err = sys.stderr
        sys.stdout = self.std_out = io.StringIO()
        sys.stderr = self.std_err = io.StringIO()

    def tearDown(self):
        sys.stdout = self.backup_out
        sys.stderr = self.backup_err

    def test_001_help(self):
        with self.assertRaises(SystemExit):
            self.arg_parser.parse_args(["--help"])
        self.assertNotEqual(self.std_out.getvalue(), "")
        self.assertEqual(self.std_err.getvalue(), "")

    def test_002_conf_file_and_api_key_mandatory(self):
        with self.assertRaises(SystemExit):
            self.arg_parser.parse_args([])
        with self.assertRaises(SystemExit):
            self.arg_parser.parse_args(["conf.json"])

    def test_003_months_worth(self):
        args = self.arg_parser.parse_args(["dummy", "xor"])
        self.assertEqual(self.std_out.getvalue(), "")
        self.assertEqual(self.std_err.getvalue(), "")
        self.assertFalse(args.week)
        self.assertEqual(args.config_json, "dummy")
        self.assertEqual(args.api_key_xor, "xor")

    def test_004_weeks_worth(self):
        args = self.arg_parser.parse_args(["--week", "dummy", "xor"])
        self.assertEqual(self.std_out.getvalue(), "")
        self.assertEqual(self.std_err.getvalue(), "")
        self.assertTrue(args.week)
        self.assertEqual(args.config_json, "dummy")
        self.assertEqual(args.api_key_xor, "xor")

    def test_005_too_many_args(self):
        for n in range(10):
            with self.assertRaises(SystemExit):
                self.arg_parser.parse_args(
                    ["dummy", "xor", "extra"] + ["extra"] * n)


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
