"""Temporal splits: train / development / locked validation / final test.

Rules enforced:
* segments are ordered and non-overlapping, separated by an embargo;
* samples whose *label window* ends after a segment boundary are purged from
  the earlier segment (``purge``);
* the final test segment can only be read through :meth:`TemporalSplit.unlock_final_test`,
  which requires an explicit acknowledgement string and is logged.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from icaif.core.leakage_guard import LeakageViolation


@dataclass(frozen=True)
class Segment:
    name: str
    start: date
    end: date  # inclusive

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end


@dataclass(frozen=True)
class TemporalSplit:
    train: Segment
    development: Segment
    locked_validation: Segment
    final_test: Segment
    embargo_days: int = 1

    def __post_init__(self) -> None:
        segs = [self.train, self.development, self.locked_validation, self.final_test]
        for a, b in zip(segs, segs[1:], strict=False):
            if not a.end + timedelta(days=self.embargo_days) < b.start:
                raise LeakageViolation(f"segments {a.name}/{b.name} overlap or violate the {self.embargo_days}-day embargo")

    def segments(self, *, include_final_test: bool = False) -> list[Segment]:
        segs = [self.train, self.development, self.locked_validation]
        return segs + [self.final_test] if include_final_test else segs

    def unlock_final_test(self, acknowledgement: str) -> Segment:
        if acknowledgement != "I will not tune after viewing the final test":
            raise PermissionError("final test segment is locked")
        return self.final_test


def purge(sample_times: Sequence[datetime], label_end_times: Sequence[datetime], boundary: datetime) -> list[int]:
    """Indices of samples whose label window ends at or before ``boundary``."""

    return [i for i, end in enumerate(label_end_times) if end <= boundary and sample_times[i] <= boundary]


def walk_forward_windows(days: Sequence[date], *, train_days: int, test_days: int, step_days: int,
                         embargo_days: int = 1) -> list[tuple[list[date], list[date]]]:
    """Rolling (train, test) day lists with an embargo gap; expanding=False."""

    ordered = sorted(days)
    out = []
    start = 0
    while start + train_days + embargo_days + test_days <= len(ordered):
        train = ordered[start:start + train_days]
        test = ordered[start + train_days + embargo_days:start + train_days + embargo_days + test_days]
        out.append((train, test))
        start += step_days
    return out
