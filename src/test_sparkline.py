#!/use/bin/env python3
import itertools
import unittest

from sparkline import *

class TestSparkline(unittest.TestCase):
    def assert_one_bar_height(self, x, bot):
        beg = "beg"
        end = "end"
        self.assertEqual("".join(itertools.chain(
            beg, LEFT_SEPARATOR, UNDEFINED if bot is None else HEIGTHS[bot], RIGHT_SEPARATOR, end)),
                         format_data(beg, [x], end))

    def test_000000_sparkline(self):
        self.assert_one_bar_height(0.0, 0)

    # Generate tests with
    # (defun fmt_test (h eps)
    #   (let ((x (+ (/ h 16.0) eps))
    #         (bot (+ (/ (- h 1) 2)
    #                 (if (> eps 0) 1 0))))
    #     (format "\n    def test_0%05d_sparkline(self):\n        self.assert_one_bar_height(%7.5f, %d)\n"
    #             (round (* 100000.0 x))
    #             x
    #             bot)))
    # (dotimes (x 8)
    #   (insert (fmt_test (1+ (* 2 x)) -0.00001))
    #   (insert (fmt_test (1+ (* 2 x)) 0.00001)))

    def test_006249_sparkline(self):
        self.assert_one_bar_height(0.06249, 0)

    def test_006251_sparkline(self):
        self.assert_one_bar_height(0.06251, 1)

    def test_018749_sparkline(self):
        self.assert_one_bar_height(0.18749, 1)

    def test_018751_sparkline(self):
        self.assert_one_bar_height(0.18751, 2)

    def test_031249_sparkline(self):
        self.assert_one_bar_height(0.31249, 2)

    def test_031251_sparkline(self):
        self.assert_one_bar_height(0.31251, 3)

    def test_043749_sparkline(self):
        self.assert_one_bar_height(0.43749, 3)

    def test_043751_sparkline(self):
        self.assert_one_bar_height(0.43751, 4)

    def test_056249_sparkline(self):
        self.assert_one_bar_height(0.56249, 4)

    def test_056251_sparkline(self):
        self.assert_one_bar_height(0.56251, 5)

    def test_068749_sparkline(self):
        self.assert_one_bar_height(0.68749, 5)

    def test_068751_sparkline(self):
        self.assert_one_bar_height(0.68751, 6)

    def test_081249_sparkline(self):
        self.assert_one_bar_height(0.81249, 6)

    def test_081251_sparkline(self):
        self.assert_one_bar_height(0.81251, 7)

    def test_093749_sparkline(self):
        self.assert_one_bar_height(0.93749, 7)

    def test_093751_sparkline(self):
        self.assert_one_bar_height(0.93751, 8)

    def test_100000_sparkline(self):
        self.assert_one_bar_height(1.0, 8)

    def test_100001_sparkline(self):
        self.assert_one_bar_height(1.00001, None)

    def test_m000001_sparkline(self):
        self.assert_one_bar_height(-0.00001, None)

    def test_m100000_sparkline(self):
        self.assert_one_bar_height(-1.0, None)

    def test_sequence_sparkline(self):
        self.assertEqual("->" + LEFT_SEPARATOR + " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588" + RIGHT_SEPARATOR + "<-",
                         format_data("->", (x / 8.001 for x in range(9)), "<-"))


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
