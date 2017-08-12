import datetime
import io
import sys
import unittest

from typing import Any

from effect import sync_perform, sync_performer, ComposedDispatcher, base_dispatcher, TypeDispatcher

import actions
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

    def test_010_satisfaction(self):
        self.assertAlmostEqual(self.make_data_1().satisfaction(), 0.5)
        self.assertAlmostEqual(self.make_data_2().satisfaction(), 0.75)
        self.assertAlmostEqual(self.make_data_3().satisfaction(), 0.833333333)


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

    def test_013_period_data(self):
        input_hours = ((1.0, 1.0),    (1.0, 2.0),   (2.0, 8.0),   (2.0, 2.0))
        # Notice the gaps in the date ranges
        input_dates = ((2016, 2, 27), (2016, 3, 2), (2016, 3, 4), (2016, 3, 4))
        acc = self.Acc.neutral()
        for hs, ds in zip(input_hours, input_dates):
            acc.update(self.Acc(datetime.date(*ds), *hs))
        data = acc.period_data()
        self.assertEqual(len(data), 7)
        self.assertAlmostEqual(data[0], 1.0)             # 27 Feb
        self.assertTrue(data[1] < 0.0 or data[1] > 1.0)  # 28 Feb
        self.assertTrue(data[2] < 0.0 or data[2] > 1.0)  # 29 Feb
        self.assertTrue(data[3] < 0.0 or data[3] > 1.0)  #  1 Mar
        self.assertAlmostEqual(data[4], 0.5)             #  2 Mar
        self.assertTrue(data[5] < 0.0 or data[5] > 1.0)  #  3 Mar
        self.assertAlmostEqual(data[6], 0.4)             #  4 Mar


class SilenceStdoutStderrMixin:
    def setUp(self):
        super().setUp()
        # Capture output to validate
        self.backup_out = sys.stdout
        self.backup_err = sys.stderr
        sys.stdout = self.std_out = io.StringIO()
        sys.stderr = self.std_err = io.StringIO()

    def tearDown(self):
        try:
            sys.stdout = self.backup_out
            sys.stderr = self.backup_err
        finally:
            super().tearDown()

    
class TestArgParse(SilenceStdoutStderrMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.arg_parser = main.make_command_line_parser()

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


class TestMain(SilenceStdoutStderrMixin, unittest.TestCase):
    class MockIO:
        today = datetime.date(2017, 6, 30)
        req_res = """Date,Comment,Hours,Activity,Issue
2017-06-20,,1.00,Other,Task #280: Automation ProjX
2017-06-20,,2.00,Other,Task #442: Scope
2017-06-20,,5.00,Planning,Task #442: Scope
2017-06-21,,3.50,Planning,Task #442: Scope
2017-06-21,,2.50,Automation,Task #318: User Story 1
2017-06-21,,2.00,Automation,Task #781: Integrate awesome lib
2017-06-22,,1.00,Automation,Task #318: User Story 1
2017-06-22,,2.00,Automation,Task #333: User Story 2
2017-06-22,,2.00,Automation,\"Task #331: User Story 2, with a twist\"
2017-06-22,,2.00,Other,Task #781: Integrate awesome lib
2017-06-23,,8.00,Other,Task #295: TRAINING
2017-06-27,,3.00,Automation,Task #333: User Story 2
2017-06-27,,4.00,Automation,\"Task #331: User Story 2, with a twist\"
2017-06-27,,1.00,Definition,Task #442: Scope
2017-06-28,,7.00,Automation,Task #333: User Story 2
2017-06-28,,1.00,Automation,Task #781: Integrate awesome lib
2017-06-24,,7.00,Automation,Task #781: Integrate awesome lib
2017-06-29,,8.00,Automation,Task #781: Integrate awesome lib
2017-06-30,,8.00,Automation,Task #781: Integrate awesome lib
2017-06-19,,1.00,Closure/Report,Task #890: Execution (build 12345)
2017-06-19,,6.00,Execution,Task #890: Execution (build 12345)
2017-06-18,,6.00,Execution,Task #890: Execution (build 12345)
2017-06-18,,2.00,Closure/Report,Task #890: Execution (build 12345)
2017-06-17,,6.00,Execution,Task #890: Execution (build 12345)
2017-06-17,,1.00,Automation,Task #890: Execution (build 12345)
"""
        config = {"api_key": "0123456789012345678901234567890123456789",
                  "host": "http://redmine.example.com",
                  "rules": [{"category": "Automation", "weight": 1.0},
                            {"issue_id": "295", "weight": 1.0},
                            {"weight": 0.0}]}

        def __init__(self):
            self.get_today_calls = 0
            self.read_config_calls = []
            self.http_requests = []
            self.lines_printed = []

        @sync_performer
        def perform_get_current_date(self, _dispatcher, _d):
            self.get_today_calls += 1
            return self.today

        @sync_performer
        def perform_http_request(self, _dispatcher, req):
            self.http_requests.append(req)
            return self.req_res

        @sync_performer
        def perform_get_config_json(self, _dispatcher, read_json):
            self.read_config_calls.append(read_json)
            return self.config

        @sync_performer
        def perform_print_line(self, _dispatcher, p):
            self.lines_printed.append(p.text)
            return None

        @property
        def dispatcher(self):
            return ComposedDispatcher([
                TypeDispatcher({
                    actions.ReadJSON: self.perform_get_config_json,
                    actions.GetCurrentDate: self.perform_get_current_date,
                    actions.HttpRequest: self.perform_http_request,
                    actions.Print: self.perform_print_line,
                }),
                base_dispatcher])

    def test_normal_run(self):
        eff = main.do_main(["config.json", "password"])
        mock_io = self.MockIO()
        result = sync_perform(mock_io.dispatcher, eff)
        self.assertIs(result, None)
        self.assertEqual(mock_io.get_today_calls, 1)
        self.assertEqual(len(mock_io.http_requests), 1)
        self.assertEqual(len(mock_io.lines_printed), 2)
        self.assertEqual(
            mock_io.lines_printed[0],
            '          \u2595\u0020\u0020\u0020\u0020\u2581\u2583\u2588\u2588'
            '\u2591\u2591\u2586\u2588\u2588\u2588\u258f\n'
            '2017-06-17\u2595\u2582\u0020\u0020\u0020\u2588\u2588\u2588\u2588'
            '\u2591\u2591\u2588\u2588\u2588\u2588\u258f2017-06-30',
        )
        self.assertRegex(
            mock_io.lines_printed[1],
            "Global satisfaction over this period: [0-9][0-9]\\.[0-9]%",
        )


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
