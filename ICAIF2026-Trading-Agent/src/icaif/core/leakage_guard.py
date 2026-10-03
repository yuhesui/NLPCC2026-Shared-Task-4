"""Point-in-time leakage guard.

Ported in spirit from AlphaAllocator ``nlpcc/core/leakage_guard.py`` but
generalised: instead of a date-level price mask plus a fixed 15:00 news
cutoff, every record carries ``available_at`` and the single invariant is

    record.available_at <= decision_time

Violations raise :class:`LeakageViolation`; there is no "warn and continue"
mode in production code. Research code that wants to *drop* future records
must call :func:`visible` explicitly, which records how many were dropped.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, TypeVar, runtime_checkable

from icaif.core.time import ensure_aware


class LeakageViolation(ValueError):
    """Raised when information not yet available at decision time is used."""


@runtime_checkable
class TimedRecord(Protocol):
    @property
    def available_at(self) -> datetime: ...

    @property
    def record_id(self) -> str: ...


T = TypeVar("T", bound=TimedRecord)


@dataclass(frozen=True)
class LeakageIssue:
    code: str
    record_id: str
    available_at: str
    decision_time: str


def find_future_records(records: Iterable[TimedRecord], decision_time: datetime) -> list[LeakageIssue]:
    cutoff = ensure_aware(decision_time, "decision_time")
    issues: list[LeakageIssue] = []
    for record in records:
        available = ensure_aware(record.available_at, "available_at")
        if available > cutoff:
            issues.append(
                LeakageIssue("future_record", record.record_id, available.isoformat(), cutoff.isoformat())
            )
    return issues


def assert_visible(records: Iterable[TimedRecord], decision_time: datetime, *, context: str = "") -> None:
    """Raise if any record became available after ``decision_time``."""

    issues = find_future_records(records, decision_time)
    if issues:
        head = "; ".join(f"{i.record_id}@{i.available_at}" for i in issues[:5])
        more = f" (+{len(issues) - 5} more)" if len(issues) > 5 else ""
        where = f" in {context}" if context else ""
        raise LeakageViolation(f"{len(issues)} record(s) available after {decision_time.isoformat()}{where}: {head}{more}")


@dataclass(frozen=True)
class VisibilityReport:
    kept: int
    dropped_future: int


def visible(records: Sequence[T], decision_time: datetime) -> tuple[list[T], VisibilityReport]:
    """Return records available at ``decision_time`` plus a drop report."""

    cutoff = ensure_aware(decision_time, "decision_time")
    kept = [r for r in records if ensure_aware(r.available_at, "available_at") <= cutoff]
    return kept, VisibilityReport(kept=len(kept), dropped_future=len(records) - len(kept))


def assert_model_cutoff(model_trained_through: datetime | None, decision_time: datetime, *, model_id: str) -> None:
    """A model fitted on data after ``decision_time`` must not score that decision.

    ``None`` means the model is a frozen public checkpoint with no
    competition-period training data; callers must pass an explicit date for
    any model fine-tuned in this repository.
    """

    if model_trained_through is None:
        return
    if ensure_aware(model_trained_through, "model_trained_through") > ensure_aware(decision_time, "decision_time"):
        raise LeakageViolation(
            f"model {model_id} trained through {model_trained_through.isoformat()} "
            f"cannot score a decision at {decision_time.isoformat()}"
        )


def assert_labels_before(label_end_times: Iterable[datetime], boundary: datetime, *, context: str) -> None:
    """Training labels must be fully realised before the split boundary (purging)."""

    cutoff = ensure_aware(boundary, "boundary")
    late = [t for t in label_end_times if ensure_aware(t, "label_end") > cutoff]
    if late:
        raise LeakageViolation(
            f"{len(late)} label window(s) end after {cutoff.isoformat()} in {context}; purge them before training"
        )
