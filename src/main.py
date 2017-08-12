import argparse
import datetime
import hashlib
from typing import Any, Dict, List, Optional, Sequence

from effect import sync_perform
from effect.do import do

import actions
import entries
import rules
import sparkline


class HoursAccumulator(rules.Accumulator):
    def __init__(self, good: float, total: float) -> None:
        self.good = good
        self.total = total

    @classmethod
    def neutral(cls):
        return cls(0, 0)

    def update(self, other: "HoursAccumulator") -> None:
        self.good += other.good
        self.total += other.total

    @classmethod
    def from_rule_and_entry(cls, rule, entry):
        return cls(rule.weight * entry.duration, entry.duration)

    def satisfaction(self) -> float:
        return self.good / self.total
    

class StampedHoursAccumulator(rules.Accumulator):
    def __init__(self, when: datetime.date, good: float, total: float) -> None:
        if good == 0.0 and total == 0.0:
            self.cal : Dict[datetime.date, HoursAccumulator] = dict()
        else:
            self.cal = {when: HoursAccumulator(good, total)}

    @classmethod
    def neutral(cls):
        # Date is ignored anyway
        return cls(datetime.date(2017, 1, 1), 0, 0)

    def update(self, other: "StampedHoursAccumulator") -> None:
        for when, hours_acc in other.cal.items():
            # This creates potentially unused HoursAccumulator instances that
            # will be garbage collected but this is a script to work on small
            # data sets, so I don't care.
            self.cal.setdefault(when, HoursAccumulator.neutral()).update(
                hours_acc)

    @classmethod
    def from_rule_and_entry(cls, rule, entry):
        return cls(entry.date, rule.weight * entry.duration, entry.duration)

    def period_start(self) -> Optional[datetime.date]:
        first = None
        for x in self.cal:
            if first is None or x < first:
                first = x
        return first

    def period_end(self) -> Optional[datetime.date]:
        last = None
        for x in self.cal:
            if last is None or x > last:
                last = x
        return last

    def period_hours_accumulator(self) -> HoursAccumulator:
        result = HoursAccumulator.neutral()
        for val in self.cal.values():
            result.update(val)
        return result

    def period_data(self) -> List[float]:
        t = self.period_start()
        stop = self.period_end()
        if t is None or stop is None:
            return []
        else:
            result = []
            NO_DATA = -1.0  # will be interpreted as missing data
            one_day = datetime.timedelta(1)  # step for iterator
            while t <= stop:
                try:
                    acc = self.cal[t]
                except KeyError:
                    val = NO_DATA
                else:
                    try:
                        val = acc.satisfaction()
                    except ZeroDivisionError:
                        val = NO_DATA
                result.append(val)
                t = one_day + t
            return result


class RuntimeInfo(object):
    "Container for runtime information.  See L{get_runtime_info}"
    # Not an @attr.s object for mypy's sake
    def __init__(
            self,
            api_key: str,
            rules: List[rules.Rule],
            start: datetime.date,
            end: datetime.date,
            base_url: str,
    ) -> None:
        self.api_key = api_key
        self.rules = rules
        self.start = start
        self.end = end
        self.base_url = base_url


def make_command_line_parser():
    parser = argparse.ArgumentParser(
        description="Query Redmine for time entries and report satisfaction")
    parser.add_argument("-w", "--week",
                        action="store_const",
                        const=True,
                        default=False,
                        help="Use last week's instead of last month's data")
    parser.add_argument("config_json",
                        help="JSON config file (api_key, host, rules list)")
    parser.add_argument("api_key_xor",
                        help="SHA256 hash of this ASCII encoded string will "
                        "be XORed with the api_key in the config_json file")
    return parser

def get_runtime_info(
        d: dict,
        api_key_xor: str,
        start: datetime.date,
        end: datetime.date
) -> RuntimeInfo:
    hash = hashlib.sha256(api_key_xor.encode("ascii")).hexdigest()
    api_key = "".join("{:02x}".format(
        int(d["api_key"][idx:idx + 2], 16) ^
        int(hash[idx:idx + 2], 16)) for idx in range(0, len(d["api_key"]), 2))
    return RuntimeInfo(api_key,
                       rules.parse_rules(d),
                       start,
                       end,
                       d["host"] + "/time_entries.csv",
    )

@do
def do_main(args_list: Sequence[str]) -> Any:
    args = make_command_line_parser().parse_args(args_list)
    config_dict = yield actions.get_config_json(args.config_json)
    now = yield actions.get_current_date()
    then = datetime.timedelta(-(7 if args.week else 31)) + now
    run_info = get_runtime_info(config_dict,
                                args.api_key_xor,
                                then,
                                now,
    )
    redmine_info = yield actions.get_redmine_info(
        run_info.base_url,
        "me", # actually the PI key identifies User
        run_info.start,
        run_info.end,
        run_info.api_key)
    redmine_entries = [x for x in entries.parse_from(redmine_info)]
    evaluator = rules.RuleEvaluator(
        rules.SelectRuleUsingTheirMatchMethod(),
        StampedHoursAccumulator)
    satisfaction = evaluator.satisfaction(run_info.rules, redmine_entries)
    yield actions.do_print(
        "{}",
        sparkline.format_data(
            str(satisfaction.period_start()),
            satisfaction.period_data(),
            str(satisfaction.period_end())))
    try:
        global_satis = satisfaction.period_hours_accumulator().satisfaction()
    except ZeroDivisionError:
        yield actions.do_print("{}", "Not enough data")
    else:
        yield actions.do_print("Global satisfaction over this period: {:.1f}%",
                               global_satis * 100.0)

def main(args_list):
    eff = do_main(args_list)
    return sync_perform(actions.IO_DISPATCHER, eff)


if __name__ == "__main__":
    main(None)
