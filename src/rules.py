"""Interpret rules to compute satisfaction score of a given time entry"""

from abc import ABCMeta, abstractmethod
import json

import attr
from typing import Any, Callable, List, Optional, Sequence, Type, TypeVar

import entries


class Rule(metaclass=ABCMeta):
    "Abstract class for mypy type declaration purposes"
    @abstractmethod
    def match(self, e: entries.TimeEntry) -> Optional[float]:
        pass

    def _validate_weight(self, attribute, value):
        attr.validators.instance_of(float)(self, attribute, value)
        if value < 0 or value > 1.0:
            raise ValueError("'{name}' must be in [0.0..1.0] and {value!r} isn't".
                             format(name=attribute.name, value=value))


@attr.s
class MatchAny(Rule):
    weight = attr.ib(validator=Rule._validate_weight)

    def match(self, e: entries.TimeEntry) -> Optional[float]:
        return self.weight


@attr.s
class MatchIssueID(Rule):
    issue_id = attr.ib(validator=attr.validators.instance_of(str))
    weight = attr.ib(validator=Rule._validate_weight)

    def match(self, e: entries.TimeEntry) -> Optional[float]:
        if e.issue_id == self.issue_id:
            return self.weight
        else:
            return None


@attr.s
class MatchCategory(Rule):
    category = attr.ib(validator=attr.validators.instance_of(str))
    weight = attr.ib(validator=Rule._validate_weight)

    def match(self, e: entries.TimeEntry) -> Optional[float]:
        if e.category == self.category:
            return self.weight
        else:
            return None


class Selector(metaclass=ABCMeta):
    """Search the sequence of rules for the rule matching the L{TimeEntry}

    Rather than passing a C{callable}, the function is wrapped in a class with
    a single L{select} method."""
    # The abstractmethod stuff is to help mypy
    @abstractmethod
    def select(self, rules: Sequence[Rule], entry: entries.TimeEntry) -> Rule:
        pass


class Accumulator(metaclass=ABCMeta):
    """Represent data with a neutral element and associative operation

    Example: (0, +) or (1, *)"""
    _C = TypeVar("_C", bound="Accumulator")
    # The abstractmethod stuff is to help mypy
    @classmethod
    @abstractmethod
    def neutral(cls: Type[_C]) -> _C:
        "Return fresh Accumulator instance that can be combined with others"
        pass

    @abstractmethod
    def update(self, other) -> None:
        pass

    @classmethod
    @abstractmethod
    def from_rule_and_entry(cls, rule: Rule, entry: entries.TimeEntry) -> "Accumulator":
        pass


class Convertor(metaclass=ABCMeta):
    """Convert a L{TimeEntry} into an L{Accumulator}

    Rather than passing a C{callable}, the function is wrapped in a class with
    a single L{select} method."""
    # The abstractmethod stuff is to help mypy
    @abstractmethod
    def convert(self, entry: entries.TimeEntry) -> Any:
        pass


class SelectRuleUsingTheirMatchMethod(Selector):
    def select(self, rules, entry):
        return next(r for r in rules if r.match(entry) is not None)


class RuleEvaluator(object):
    AccumulatorType = TypeVar("AccumulatorType", bound=Accumulator)
    def __init__(self, selector: Selector, accumulator: Type[AccumulatorType]) -> None:
        if hasattr(selector, "select"):
            self.selector = selector
        else:
            raise TypeError("selector argument should have a `select' method")
        acc_methods = ("neutral", "update", "from_rule_and_entry")
        if all(hasattr(accumulator, a) for a in acc_methods):
            self.accumulator = accumulator
        else:
            raise TypeError(
                "accumulator argument should have {} methods".format(
                    acc_methods))

    def satisfaction(
            self,
            rules: Sequence[Rule],
            entries: Sequence[entries.TimeEntry]
    ) -> AccumulatorType:
        acc = self.accumulator.neutral()
        for entry in entries:
            r = self.selector.select(rules, entry)
            acc.update(self.accumulator.from_rule_and_entry(r, entry))
        return acc


def _extract_keys_and_construct(
        d: dict, ks: Sequence[str], ctor: Callable[..., Rule]) -> Optional[Rule]:
    ignored_key_count = 1 if "_comment" in d else 0
    key_count = len(ks)
    if key_count + ignored_key_count == len(d):
        try:
            values = [d[key] for key in ks]
        except KeyError:
            return None
        else:
            return ctor(*values)
    else:
        return None

def parse_rules(d: dict) -> List[Rule]:
    return [next(x
                 for x in (_extract_keys_and_construct(elt, keys, ctor)
                           for (keys, ctor) in ((["issue_id", "weight"], MatchIssueID),
                                                (["category", "weight"], MatchCategory),
                                                (["weight"], MatchAny),
                           ))
                 if x is not None)
            for elt in d["rules"]]
