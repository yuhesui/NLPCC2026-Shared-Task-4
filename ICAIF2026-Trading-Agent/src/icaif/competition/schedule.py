"""Round schedule: parse the organizer schedule or generate the standard one.

The organizer's live schedule (``GET /api/v1/schedule``) is authoritative; the
generator reproduces the *standard* calendar from the rules for backtests and
offline tests, and is cross-checked against the bundled official
``schedule.json`` in ``tests/competition/test_official_kit_parity.py``.

Window semantics (docs/rules.md): a window includes ``opens_at`` and excludes
``deadline``. The R1 window opens 10 minutes after the previous trading day's
last active execution (normally 15:40 ET); R2..R7 open 10 minutes after the
preceding execution.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from icaif.core.constants import (
    PHASES,
    REGULAR_CLOSE_ET,
    ROUND_DEADLINES_ET,
    ROUND_EXECUTION_TIMES_ET,
    ROUND_ID_PATTERN,
    UPLOAD_DELAY_MINUTES,
)
from icaif.core.time import et_datetime, parse_timestamp

_ROUND_ID = re.compile(ROUND_ID_PATTERN)


class ScheduleError(ValueError):
    pass


class DeadlineError(RuntimeError):
    """Raised when a submission would be outside (or too close to) its window."""


@dataclass(frozen=True)
class Round:
    id: str
    phase: str
    day: date
    number: int
    opens_at: datetime
    deadline: datetime
    execution_time: datetime
    close_time: datetime
    status: str = "SCHEDULED"

    def __post_init__(self) -> None:
        if not _ROUND_ID.match(self.id):
            raise ScheduleError(f"invalid round id {self.id!r}")
        if self.phase not in PHASES:
            raise ScheduleError(f"invalid phase {self.phase!r}")
        if not self.id.startswith(f"{self.phase}-{self.day.isoformat()}-r{self.number}"):
            raise ScheduleError(f"round id {self.id!r} inconsistent with phase/day/number")
        if not self.opens_at < self.deadline <= self.execution_time <= self.close_time:
            raise ScheduleError(f"round {self.id} has inconsistent timestamps")

    @property
    def cancelled(self) -> bool:
        return self.status == "CANCELLED"

    def window_contains(self, when: datetime) -> bool:
        return self.opens_at <= when < self.deadline

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> Round:
        try:
            return cls(
                id=str(row["id"]),
                phase=str(row["phase"]),
                day=date.fromisoformat(str(row["day"])),
                number=int(row["number"]),
                opens_at=parse_timestamp(row["opens_at"], "opens_at"),
                deadline=parse_timestamp(row["deadline"], "deadline"),
                execution_time=parse_timestamp(row["execution_time"], "execution_time"),
                close_time=parse_timestamp(row["close_time"], "close_time"),
                status=str(row.get("status", "SCHEDULED")),
            )
        except (KeyError, TypeError) as error:
            raise ScheduleError(f"malformed round row: {error}") from error

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "phase": self.phase,
            "day": self.day.isoformat(),
            "number": self.number,
            "opens_at": self.opens_at.isoformat(),
            "deadline": self.deadline.isoformat(),
            "execution_time": self.execution_time.isoformat(),
            "close_time": self.close_time.isoformat(),
            "status": self.status,
        }


def parse_round_id(round_id: str) -> tuple[str, date, int]:
    match = re.fullmatch(r"(validation|official)-(\d{4}-\d{2}-\d{2})-r([1-7])", round_id)
    if not match:
        raise ScheduleError(f"invalid round id {round_id!r}")
    return match[1], date.fromisoformat(match[2]), int(match[3])


@dataclass(frozen=True)
class Schedule:
    rounds: tuple[Round, ...]
    source: str = "generated"

    def __post_init__(self) -> None:
        ids = [r.id for r in self.rounds]
        if len(ids) != len(set(ids)):
            raise ScheduleError("duplicate round ids in schedule")
        object.__setattr__(self, "rounds", tuple(sorted(self.rounds, key=lambda r: r.execution_time)))

    @classmethod
    def from_official(cls, payload: Mapping[str, Any], source: str = "official") -> Schedule:
        rows = payload.get("rounds")
        if not isinstance(rows, list) or not rows:
            raise ScheduleError("schedule contains no rounds")
        return cls(tuple(Round.from_mapping(row) for row in rows), source=source)

    def phase_rounds(self, phase: str, *, include_cancelled: bool = False) -> list[Round]:
        return [r for r in self.rounds if r.phase == phase and (include_cancelled or not r.cancelled)]

    def get(self, round_id: str) -> Round:
        for row in self.rounds:
            if row.id == round_id:
                return row
        raise ScheduleError(f"unknown round {round_id!r}")

    def active_round(self, now: datetime, phase: str) -> Round | None:
        """The (non-cancelled) round whose upload window contains ``now``."""

        for row in self.phase_rounds(phase):
            if row.window_contains(now):
                return row
        return None

    def next_round(self, now: datetime, phase: str) -> Round | None:
        upcoming = [r for r in self.phase_rounds(phase) if r.deadline > now]
        return min(upcoming, key=lambda r: r.deadline) if upcoming else None

    def trading_days(self, phase: str) -> list[date]:
        return sorted({r.day for r in self.phase_rounds(phase)})


def generate_standard_schedule(phase: str, days: Sequence[date] | Iterable[date]) -> Schedule:
    """Standard seven-round calendar on the given trading days (no early closes)."""

    day_list = sorted(set(days))
    rounds: list[Round] = []
    previous_last_execution: datetime | None = None
    for day in day_list:
        close = et_datetime(day, REGULAR_CLOSE_ET)
        executions = [et_datetime(day, t) for t in ROUND_EXECUTION_TIMES_ET]
        deadlines = [et_datetime(day, t) for t in ROUND_DEADLINES_ET]
        for idx in range(7):
            if idx == 0:
                # Previous trading day's last execution + 10 min. For the first
                # day of a phase the organizer uses the prior calendar trading
                # day; approximate with the previous weekday 15:40 ET.
                anchor = previous_last_execution or _previous_weekday_last_execution(day)
                opens = anchor + timedelta(minutes=UPLOAD_DELAY_MINUTES)
            else:
                opens = executions[idx - 1] + timedelta(minutes=UPLOAD_DELAY_MINUTES)
            rounds.append(
                Round(
                    id=f"{phase}-{day.isoformat()}-r{idx + 1}",
                    phase=phase,
                    day=day,
                    number=idx + 1,
                    opens_at=opens,
                    deadline=deadlines[idx],
                    execution_time=executions[idx],
                    close_time=close,
                )
            )
        previous_last_execution = executions[-1]
    return Schedule(tuple(rounds), source="generated-standard")


def _previous_weekday_last_execution(day: date) -> datetime:
    prev = day - timedelta(days=1)
    while prev.weekday() >= 5:
        prev -= timedelta(days=1)
    return et_datetime(prev, ROUND_EXECUTION_TIMES_ET[-1])


def assert_submission_window(row: Round, now: datetime, *, safety_margin: timedelta = timedelta(0)) -> None:
    """Deadline guard: refuse to submit outside the window or inside the margin.

    The platform's *upload* timestamp decides timeliness, so the margin should
    cover worker/network latency (configs/execution/live.yaml).
    """

    if row.cancelled:
        raise DeadlineError(f"round {row.id} is cancelled")
    if now < row.opens_at:
        raise DeadlineError(f"round {row.id} window not open until {row.opens_at.isoformat()}")
    if now + safety_margin >= row.deadline:
        raise DeadlineError(
            f"round {row.id} deadline {row.deadline.isoformat()} too close or passed (now={now.isoformat()}, "
            f"margin={safety_margin})"
        )
