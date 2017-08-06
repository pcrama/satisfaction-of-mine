#!/use/bin/env python3
import itertools
import unittest

from sparkline import *

class TestSparkline(unittest.TestCase):
    def assert_one_bar_height(self, x, top, bot):
        beg = "beg"
        end = "end"
        self.assertEqual("".join(itertools.chain(
            " " * len(beg), LEFT_SEPARATOR, UNDEFINED if top is None else HEIGTHS[top], RIGHT_SEPARATOR, "\n",
            beg, LEFT_SEPARATOR, UNDEFINED if bot is None else HEIGTHS[bot], RIGHT_SEPARATOR, end)),
                         format_data(beg, [x], end))

    def test_000000_sparkline(self):
        self.assert_one_bar_height(0.0, 0, 0)

    # Generate tests with
    # (defun fmt_test (h eps)
    #   (let ((x (+ (/ h 32.0) eps))
    #         (bot (if (> h 16)
    #                  8
    #                (+ (/ (- h 1) 2)
    #                   (if (> eps 0) 1 0))))
    #         (top (if (> h 16)
    #                  (+ (/ (- h 17) 2)
    #                     (if (> eps 0) 1 0))
    #                0)))
    #     (format "\n    def test_0%05d_sparkline(self):\n        self.assert_one_bar_height(%7.5f, %d, %d)\n"
    #             (round (* 100000.0 x))
    #             x
    #             top
    #             bot)))
    # (dotimes (x 16)
    #   (insert (fmt_test (1+ (* 2 x)) -0.00001))
    #   (insert (fmt_test (1+ (* 2 x)) 0.00001)))

    def test_003124_sparkline(self):
        self.assert_one_bar_height(0.03124, 0, 0)

    def test_003126_sparkline(self):
        self.assert_one_bar_height(0.03126, 0, 1)

    def test_009374_sparkline(self):
        self.assert_one_bar_height(0.09374, 0, 1)

    def test_009376_sparkline(self):
        self.assert_one_bar_height(0.09376, 0, 2)

    def test_015624_sparkline(self):
        self.assert_one_bar_height(0.15624, 0, 2)

    def test_015626_sparkline(self):
        self.assert_one_bar_height(0.15626, 0, 3)

    def test_021874_sparkline(self):
        self.assert_one_bar_height(0.21874, 0, 3)

    def test_021876_sparkline(self):
        self.assert_one_bar_height(0.21876, 0, 4)

    def test_028124_sparkline(self):
        self.assert_one_bar_height(0.28124, 0, 4)

    def test_028126_sparkline(self):
        self.assert_one_bar_height(0.28126, 0, 5)

    def test_034374_sparkline(self):
        self.assert_one_bar_height(0.34374, 0, 5)

    def test_034376_sparkline(self):
        self.assert_one_bar_height(0.34376, 0, 6)

    def test_040624_sparkline(self):
        self.assert_one_bar_height(0.40624, 0, 6)

    def test_040626_sparkline(self):
        self.assert_one_bar_height(0.40626, 0, 7)

    def test_046874_sparkline(self):
        self.assert_one_bar_height(0.46874, 0, 7)

    def test_046876_sparkline(self):
        self.assert_one_bar_height(0.46876, 0, 8)

    def test_053124_sparkline(self):
        self.assert_one_bar_height(0.53124, 0, 8)

    def test_053126_sparkline(self):
        self.assert_one_bar_height(0.53126, 1, 8)

    def test_059374_sparkline(self):
        self.assert_one_bar_height(0.59374, 1, 8)

    def test_059376_sparkline(self):
        self.assert_one_bar_height(0.59376, 2, 8)

    def test_065624_sparkline(self):
        self.assert_one_bar_height(0.65624, 2, 8)

    def test_065626_sparkline(self):
        self.assert_one_bar_height(0.65626, 3, 8)

    def test_071874_sparkline(self):
        self.assert_one_bar_height(0.71874, 3, 8)

    def test_071876_sparkline(self):
        self.assert_one_bar_height(0.71876, 4, 8)

    def test_078124_sparkline(self):
        self.assert_one_bar_height(0.78124, 4, 8)

    def test_078126_sparkline(self):
        self.assert_one_bar_height(0.78126, 5, 8)

    def test_084374_sparkline(self):
        self.assert_one_bar_height(0.84374, 5, 8)

    def test_084376_sparkline(self):
        self.assert_one_bar_height(0.84376, 6, 8)

    def test_090624_sparkline(self):
        self.assert_one_bar_height(0.90624, 6, 8)

    def test_090626_sparkline(self):
        self.assert_one_bar_height(0.90626, 7, 8)

    def test_096874_sparkline(self):
        self.assert_one_bar_height(0.96874, 7, 8)

    def test_096876_sparkline(self):
        self.assert_one_bar_height(0.96876, 8, 8)

    def test_100000_sparkline(self):
        self.assert_one_bar_height(1.0, 8, 8)

    def test_m100000_sparkline(self):
        self.assert_one_bar_height(-1.0, None, None)

    def test_sequence_sparkline(self):
        self.assertEqual("  " + LEFT_SEPARATOR + (9 * " ") + "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588" + RIGHT_SEPARATOR + "\n" +
                         "->" + LEFT_SEPARATOR + " \u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588" + (8 * "\u2588") + RIGHT_SEPARATOR + "<-",
                         format_data("->", (x / 16.001 for x in range(17)), "<-"))


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
