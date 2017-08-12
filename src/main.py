import argparse
import datetime
import hashlib
from typing import Dict, List, Optional

from effect.do import do

import actions
import rules


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
    

class StampedHoursAccumulator(rules.Accumulator):
    def __init__(self, when: datetime.date, good: float, total: float) -> None:
        if good == 0.0 and total == 0.0:
            self.cal : Dict[datetime.date, HoursAccumulator] = dict()
        else:
            self.cal = {when: HoursAccumulator(good, total)}

    @classmethod
    def neutral(cls):
        return cls(datetime.date.today(), 0, 0)

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
def main(args_list):
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
        "me", # actually API key identifies User
        run_info.start,
        run_info.end,
        run_info.api_key)

if __name__ == "__main__":
    main(None)
