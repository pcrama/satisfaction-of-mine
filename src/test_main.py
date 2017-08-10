import datetime
import io
import sys
import unittest

from typing import Any

import main

class BaseAccumulatorTestMixin():
    """Add this class to your C{TestCase}: easily define Accumulator unittests

    Define L{Acc}; override L{make_data_1}, L{make_data_2}, L{make_data_3} and
    L{assert_accumulator_equal}."""
    def make_data_1(self):
        raise NotImplementedError()

    def make_data_2(self):
        raise NotImplementedError()

    def make_data_3(self):
        raise NotImplementedError()

    def assert_accumulator_equal(self, a, b):
        raise NotImplementedError()

    def make_all(self):
        return (self.make_data_1(),
                self.make_data_2(),
                self.make_data_3())

    def test_001_equality(self):
        # This is probably more of a validation of assert_accumulator_equal
        "x = x"
        self.assert_accumulator_equal(self.Acc.neutral(),
                                      self.Acc.neutral())
        for x, y in zip(self.make_all(), self.make_all()):
            self.assert_accumulator_equal(x, y)

    def test_002_neutral_plus_neutral(self):
        "0 + 0 = 0"
        a = self.Acc.neutral()
        b = self.Acc.neutral()
        a.update(b)
        self.assert_accumulator_equal(self.Acc.neutral(), a)
        self.assert_accumulator_equal(self.Acc.neutral(), b)

    def test_003_neutral_plus_any(self):
        "x + 0 = x and 0 + x = x"
        for x, y in zip(self.make_all(), self.make_all()):
            x.update(self.Acc.neutral())
            self.assert_accumulator_equal(x, y)
            c = self.Acc.neutral()
            c.update(y)
            self.assert_accumulator_equal(x, y)

    def test_004_associative(self):
        "(x + y) + z = x + (y + z)"
        x, y, z = self.make_all()
        a, b, c = self.make_all()
        x.update(y)  # x' <- x + y
        x.update(z)  # x'' <- x' + z = (x + y) + z
        b.update(c)  # b' <- b + c
        a.update(b)  # a' <- a + b' = a + (b + c)
        self.assert_accumulator_equal(x, a)


def _assert_accumulator_equal(testcase, a, b):
    testcase.assertAlmostEqual(a.good, b.good)
    testcase.assertAlmostEqual(a.total, b.total)


class TestHoursAccumulator(unittest.TestCase, BaseAccumulatorTestMixin):
    Acc = main.HoursAccumulator

    def make_data_1(self):
        return self.Acc(1.0, 2.0)

    def make_data_2(self):
        return self.Acc(3.0, 4.0)

    def make_data_3(self):
        return self.Acc(5.0, 6.0)

    def assert_accumulator_equal(self, a, b):
        _assert_accumulator_equal(self, a, b)


class TestStampedHoursAccumulator(unittest.TestCase, BaseAccumulatorTestMixin):
    Acc = main.StampedHoursAccumulator

    def make_data_1(self):
        return self.Acc(datetime.date(2017, 1, 1), 1.0, 2.0)

    def make_data_2(self):
        result =      self.Acc(datetime.date(2016, 1, 2), 3.0 , 4.0 )
        result.update(self.Acc(datetime.date(2017, 1, 1), 3.5 , 4.5 ))
        result.update(self.Acc(datetime.date(2017, 1, 2), 3.25, 4.75))
        result.update(self.Acc(datetime.date(2017, 2, 1), 3.75, 4.25))
        return result

    def make_data_3(self):
        result = self.Acc(datetime.date(2017, 1, 2), 5.0, 6.0)
        result.update(self.Acc(datetime.date(2017, 1, 1), 7.0, 8.0))
        return result

    def assert_accumulator_equal(self, a, b):
        self.assertEqual(len(a.cal), len(b.cal))
        for when, hours_acc in a.cal.items():
            _assert_accumulator_equal(self, hours_acc, b.cal[when])

    def test_010_period_start(self):
        self.assertEqual(self.make_data_1().period_start(),
                         datetime.date(2017, 1, 1))
        self.assertEqual(self.make_data_2().period_start(),
                         datetime.date(2016, 1, 2))
        self.assertEqual(self.make_data_3().period_start(),
                         datetime.date(2017, 1, 1))
        self.assertIsNone(self.Acc.neutral().period_start())

    def test_011_period_end(self):
        self.assertEqual(self.make_data_1().period_end(),
                         datetime.date(2017, 1, 1))
        self.assertEqual(self.make_data_2().period_end(),
                         datetime.date(2017, 2, 1))
        self.assertEqual(self.make_data_3().period_end(),
                         datetime.date(2017, 1, 2))
        self.assertIsNone(self.Acc.neutral().period_end())

    def test_012_period_hours_accumulator(self):
        x, y, z = self.make_all()
        _assert_accumulator_equal(
            self,
            main.HoursAccumulator.neutral(),
            self.Acc.neutral().period_hours_accumulator())
        _assert_accumulator_equal(
            self,
            main.HoursAccumulator(1.0, 2.0),
            x.period_hours_accumulator())
        _assert_accumulator_equal(
            self,
            main.HoursAccumulator(3.0 + 3.5 + 3.25 + 3.75,
                                  4.0 + 4.5 + 4.75 + 4.25),
            y.period_hours_accumulator())
        _assert_accumulator_equal(
            self,
            main.HoursAccumulator(5.0 + 7.0, 6.0 + 8.0),
            z.period_hours_accumulator())

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
