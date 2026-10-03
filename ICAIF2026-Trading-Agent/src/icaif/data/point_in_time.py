"""Point-in-time stores: the only way decision code reads timed records.

``PITStore.as_of(t)`` returns records with ``available_at <= t``. Stores never
hand out the full history to decision code; simulators may read it via
``all_records`` (named loudly on purpose).

``MacroStore`` adds vintage semantics: for each (series, reference period) it
returns the latest vintage *released by* ``t`` — a revision published after
``t`` cannot leak backwards.

``FilingStore`` keeps amended filings as separate records; an amendment never
replaces what was visible before its own acceptance time.
"""

from __future__ import annotations

import bisect
from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Generic, TypeVar

from icaif.core.leakage_guard import TimedRecord, assert_visible
from icaif.core.schemas import Filing, MacroObservation
from icaif.core.time import ensure_aware

R = TypeVar("R", bound=TimedRecord)


class PITStore(Generic[R]):
    def __init__(self, records: Iterable[R] = ()) -> None:
        self._records: list[R] = []
        self._times: list[datetime] = []
        self._ids: set[str] = set()
        self.extend(records)

    def extend(self, records: Iterable[R]) -> None:
        for record in records:
            if record.record_id in self._ids:
                continue  # exact duplicate id: idempotent ingest
            available = ensure_aware(record.available_at, "available_at")
            idx = bisect.bisect_right(self._times, available)
            self._times.insert(idx, available)
            self._records.insert(idx, record)
            self._ids.add(record.record_id)

    def __len__(self) -> int:
        return len(self._records)

    def as_of(self, decision_time: datetime) -> list[R]:
        cutoff = ensure_aware(decision_time, "decision_time")
        idx = bisect.bisect_right(self._times, cutoff)
        out = self._records[:idx]
        assert_visible(out, cutoff, context="PITStore.as_of")  # defensive: invariant check
        return out

    def window(self, decision_time: datetime, lookback_start: datetime) -> list[R]:
        start = ensure_aware(lookback_start, "lookback_start")
        return [r for r in self.as_of(decision_time) if r.available_at >= start]

    @property
    def all_records(self) -> Sequence[R]:
        """Full history, *simulator use only* (never pass to decision code)."""

        return tuple(self._records)


class MacroStore(PITStore[MacroObservation]):
    def latest(self, series_id: str, decision_time: datetime) -> dict[datetime, MacroObservation]:
        """Latest visible vintage per reference period for ``series_id``."""

        best: dict[datetime, MacroObservation] = {}
        for obs in self.as_of(decision_time):
            if obs.series_id != series_id:
                continue
            current = best.get(obs.event_time)
            if current is None or obs.available_at >= current.available_at:
                best[obs.event_time] = obs
        return dict(sorted(best.items()))

    def latest_value(self, series_id: str, decision_time: datetime) -> MacroObservation | None:
        vintages = self.latest(series_id, decision_time)
        return vintages[max(vintages)] if vintages else None


class FilingStore(PITStore[Filing]):
    def for_ticker(self, ticker: str, decision_time: datetime, *, forms: Iterable[str] | None = None) -> list[Filing]:
        wanted = {f.upper() for f in forms} if forms else None
        return [
            f
            for f in self.as_of(decision_time)
            if f.ticker == ticker and (wanted is None or f.form.upper() in wanted)
        ]
