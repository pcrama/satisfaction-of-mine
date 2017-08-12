#!/usr/bin/env python3
import unittest

import attr

import entries
import rules

def _make_TimeEntry(issue_id="12345", duration=1.0, category="Test",
                    comment="", date="2017-07-26"):
    return entries.TimeEntry(issue_id, duration, category, comment, date)


class TestMatchIssueID(unittest.TestCase):
    def test_001_create_MatchIssueID(self):
        "You can create a rule matching a precise issue ID but only using a str"
        with self.assertRaisesRegex(TypeError, "issue_id"):
            r = rules.MatchIssueID(1234, 1.0)

    def test_002_create_MatchIssueID(self):
        "You can create a rule matching a precise issue ID"
        r = rules.MatchIssueID("01234", 1.0)

    def test_003_create_MatchIssueID(self):
        "MatchIssueID validates the weight attribute"
        param = "weight"
        create_with_weight = lambda w: rules.MatchIssueID("1234", w)
        with self.assertRaisesRegex(TypeError, "weight"):
            r = create_with_weight(None)
        with self.assertRaisesRegex(ValueError, "weight"):
            r = create_with_weight(-0.1)
        with self.assertRaisesRegex(ValueError, "weight"):
            r = create_with_weight(1.1)

    def test_100_use_MatchIssueID(self):
        "A matching issue ID in a time entry is recognized"
        issue_id = "12345"
        weight = 0.23
        r = rules.MatchIssueID(issue_id, weight)
        e = _make_TimeEntry(issue_id=issue_id)
        self.assertEqual(weight, r.match(e))

    def test_101_use_MatchIssueID(self):
        "A mismatching issue ID in a time entry is rejected"
        r = rules.MatchIssueID("12345", 1.0)
        e = _make_TimeEntry(issue_id="6789")
        self.assertIs(None, r.match(e))


class TestMatchCategory(unittest.TestCase):
    def test_001_create_MatchCategory(self):
        "MatchCategory validates its target category"
        with self.assertRaisesRegex(TypeError, "category"):
            r = rules.MatchCategory(1234, 1.0)

    def test_002_create_MatchCategory(self):
        r = rules.MatchCategory("Automation", 1.0)

    def test_003_create_MatchCategory(self):
        "MatchCategory validates its weight"
        with self.assertRaisesRegex(TypeError, "weight"):
            r = rules.MatchCategory("Automation", None)

    def test_004_create_MatchCategory(self):
        "MatchCategory validates its weight"
        with self.assertRaisesRegex(ValueError, "weight"):
            r = rules.MatchCategory("Automation", -0.1)
        with self.assertRaisesRegex(ValueError, "weight"):
            r = rules.MatchCategory("Automation", 1.1)

    def test_100_use_MatchCategory(self):
        "A matching category in a time entry is recognized"
        category = "12345"
        r = rules.MatchCategory(category, 1.0)
        e = _make_TimeEntry(category=category)
        self.assertTrue(r.match(e))

    def test_101_use_MatchCategory(self):
        "A mismatching category in a time entry is rejected"
        r = rules.MatchCategory("12345", 1.0)
        e = _make_TimeEntry(category="6789")
        self.assertFalse(r.match(e))


@attr.s
class _DummyAccumulator(rules.Accumulator):
    x = attr.ib(default=[])

    @classmethod
    def neutral(cls):
        return cls([])
    
    def update(self, other: "_DummyAccumulator") -> None:
        self.x.extend(other.x)

    @classmethod
    def from_rule_and_entry(cls, rule, entry):
        return cls([(rule, entry)])


class _DummySelector(rules.Selector):
    def select(self, rules, entry):
        return next(r for r in rules if r.match(entry))


class TestRuleEvaluator(unittest.TestCase):
    def test_001_create_RuleEvaluator(self):
        "RuleEvaluator validates its `selector' parameter"
        with self.assertRaisesRegex(TypeError, "selector"):
            rules.RuleEvaluator(0, _DummyAccumulator)

    def test_002_create_RuleEvaluator(self):
        "RuleEvaluator validates its `accumulator' parameter"
        with self.assertRaisesRegex(TypeError, "accumulator"):
            rules.RuleEvaluator(_DummySelector(), 0)

    def test_003_create_RuleEvaluator(self):
        "Create a RuleEvaluator"
        rules.RuleEvaluator(_DummySelector(), _DummyAccumulator)

    def test_004_use_RuleEvaluator(self):
        rulz = [rules.MatchIssueID("65432", 0.9),
                rules.MatchCategory("Automation", 1.0),
                rules.MatchIssueID("12345", 0.6),
                rules.MatchAny(0.5)]
        entrz = [entries.TimeEntry("12345", 1.0, "Automation", "", "2017-07-29"),
                 entries.TimeEntry("12345", 1.0, "Other", "", "2017-07-29"),
                 entries.TimeEntry("65432", 1.0, "Other", "", "2017-07-29"),
                 entries.TimeEntry("76543", 1.0, "Automation", "", "2017-07-29"),
                 entries.TimeEntry("65432", 1.0, "Automation", "", "2017-07-29"),
                 entries.TimeEntry("76543", 1.0, "Other", "", "2017-07-29")]
        evaluator = rules.RuleEvaluator(_DummySelector(), _DummyAccumulator)
        self.assertEqual([(rulz[1], entrz[0]),
                          (rulz[2], entrz[1]),
                          (rulz[0], entrz[2]),
                          (rulz[1], entrz[3]),
                          (rulz[0], entrz[4]),
                          (rulz[3], entrz[5])],
                         evaluator.satisfaction(rulz, entrz).x)


class TestParseRules(unittest.TestCase):
    def assert_parse_rules(self, rules_list, expected):
        self.assertEqual(rules.parse_rules({"rules": rules_list}), expected)

    def test_001_empty_rules_list(self):
        self.assert_parse_rules([], [])

    def test_002_no_rules_raises(self):
        self.assertRaises(KeyError, rules.parse_rules, {})

    def test_003_1_rule_match_id(self):
        issue_id = "12345"
        weight = 0.5
        self.assert_parse_rules([{"issue_id": issue_id, "weight": weight}],
                                [rules.MatchIssueID(issue_id, weight)])

    def test_004_2_rules_match_id(self):
        issue_id = "12345", "67890"
        weight = 0.5, 1.0
        self.assert_parse_rules([{"issue_id": issue_id[idx], "weight": weight[idx]}
                                 for idx in range(len(issue_id))],
                                [rules.MatchIssueID(issue_id[idx], weight[idx])
                                 for idx in range(len(issue_id))])

    def test_005_1_rule_match_any(self):
        weight = 0.5
        self.assert_parse_rules([{"weight": weight}], [rules.MatchAny(weight)])

    def test_006_1_rule_match_category(self):
        category = "Automation"
        weight = 0.75
        self.assert_parse_rules([{"category": category, "weight": weight}],
                                [rules.MatchCategory(category, weight)])

    def test_007_mix_of_rules(self):
        issue_id = "111222"
        weight_id = 0.3
        category = "Other"
        weight_category = 0.6
        weight_any = 0.9
        self.assert_parse_rules([{"issue_id": issue_id, "weight": weight_id},
                                 {"category": category, "weight": weight_category},
                                 {"weight": weight_any}],
                                [rules.MatchIssueID(issue_id, weight_id),
                                 rules.MatchCategory(category, weight_category),
                                 rules.MatchAny(weight_any)])

    def test_008_extra_keys_raise(self):
        self.assertRaises(Exception,
                          rules.parse_rules,
                          {"rules": [{"issue_id": "1", "weight": 0.0, "extra": "raises"}]})

if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, exit=not hasattr(sys, "ps1"))
