"""Interpret rules to compute satisfaction score of a given time entry"""

from abc import ABCMeta, abstractmethod

import attr
from typing import Any, Optional, Sequence, TypeVar

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

    def match(self, e):
        return self.weight


@attr.s
class MatchIssueID(Rule):
    issue_id = attr.ib(validator=attr.validators.instance_of(str))
    weight = attr.ib(validator=Rule._validate_weight)

    def match(self, e):
        if e.issue_id == self.issue_id:
            return self.weight


@attr.s
class MatchCategory(Rule):
    category = attr.ib(validator=attr.validators.instance_of(str))
    weight = attr.ib(validator=Rule._validate_weight)

    def match(self, e):
        return e.category == self.category


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
    # The abstractmethod stuff is to help mypy
    @classmethod
    @abstractmethod
    def neutral(cls) -> "Accumulator":
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


@attr.s
class RuleEvaluator(object):
    selector = attr.ib(validator=attr.validators.instance_of(Selector))
    accumulator = attr.ib(validator=attr.validators.instance_of(Accumulator))

    def satisfaction(self, rules: Sequence[Rule], entries: Sequence[entries.TimeEntry]) -> Accumulator:
        acc = self.accumulator.neutral()
        for entry in entries:
            r = self.selector.select(rules, entry)
            acc.update(self.accumulator.from_rule_and_entry(r, entry))
        return acc
