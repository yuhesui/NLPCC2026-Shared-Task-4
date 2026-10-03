"""Aligned bar panel (time x 30 symbols) with point-in-time views.

Bars are completed intervals ``[start, end)`` at a fixed ``bar_minutes``
frequency during regular hours. ``available_at`` (per row) is the time the
completed bar could be read. Decision code receives a :class:`MarketView`
built by :meth:`MarketPanel.as_of`, which contains only rows with
``available_at <= decision_time`` — a partially formed bar is never visible.

Note on alignment: with 60-minute bars aligned to the :30 executions, the bar
that *contains* a round's deadline is not complete at the deadline, so the
last visible bar at R2..R7 is one hour stale. Finer bars (e.g. 30-minute or
5-minute) reduce that staleness; the panel supports any fixed frequency.
"""

from __future__ import annotations

import bisect
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import numpy as np

from icaif.core.leakage_guard import LeakageViolation
from icaif.core.schemas import MarketBar
from icaif.core.time import ensure_aware, et_date
from icaif.core.universe import SYMBOL_INDEX, SYMBOLS

TRADING_MINUTES_PER_DAY = 390


@dataclass(frozen=True)
class MarketPanel:
    starts: tuple[datetime, ...]
    ends: tuple[datetime, ...]
    available_at: tuple[datetime, ...]
    open: np.ndarray  # shape (T, N); NaN = missing bar for that symbol
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    bar_minutes: int
    source: str
    synthetic: bool

    def __post_init__(self) -> None:
        t = len(self.starts)
        for name in ("open", "high", "low", "close", "volume"):
            arr = getattr(self, name)
            if arr.shape != (t, len(SYMBOLS)):
                raise ValueError(f"{name} must have shape ({t}, {len(SYMBOLS)})")
            arr.setflags(write=False)
        if len(self.ends) != t or len(self.available_at) != t:
            raise ValueError("time axes must have equal length")
        if any(b <= a for a, b in zip(self.ends, self.ends[1:], strict=False)):
            raise ValueError("bar ends must be strictly increasing")
        if any(av < end for av, end in zip(self.available_at, self.ends, strict=True)):
            raise ValueError("available_at must not precede bar end")

    # -- construction -----------------------------------------------------
    @classmethod
    def from_bars(cls, bars: Iterable[MarketBar], *, bar_minutes: int, synthetic: bool) -> MarketPanel:
        rows: dict[datetime, dict[str, MarketBar]] = {}
        sources: set[str] = set()
        for bar in bars:
            if bar.symbol not in SYMBOL_INDEX:
                raise ValueError(f"unknown symbol {bar.symbol}")
            if (bar.end - bar.start) != timedelta(minutes=bar_minutes) and not _is_session_tail(bar, bar_minutes):
                raise ValueError(f"bar {bar.record_id} does not match bar_minutes={bar_minutes}")
            slot = rows.setdefault(bar.start, {})
            if bar.symbol in slot:
                raise ValueError(f"duplicate bar {bar.record_id}")
            slot[bar.symbol] = bar
            sources.add(bar.provenance.source)
        starts = sorted(rows)
        t, n = len(starts), len(SYMBOLS)
        arrays = {k: np.full((t, n), np.nan) for k in ("open", "high", "low", "close", "volume")}
        ends: list[datetime] = []
        avail: list[datetime] = []
        for i, start in enumerate(starts):
            slot = rows[start]
            ends_i = {b.end for b in slot.values()}
            if len(ends_i) != 1:
                raise ValueError(f"inconsistent bar ends at {start}")
            ends.append(ends_i.pop())
            avail.append(max(b.available_at for b in slot.values()))
            for symbol, bar in slot.items():
                j = SYMBOL_INDEX[symbol]
                for k in arrays:
                    arrays[k][i, j] = getattr(bar, k)
        return cls(
            starts=tuple(starts),
            ends=tuple(ends),
            available_at=tuple(avail),
            bar_minutes=bar_minutes,
            source="+".join(sorted(sources)),
            synthetic=synthetic,
            **arrays,
        )

    # -- point-in-time ----------------------------------------------------
    def as_of(self, decision_time: datetime) -> MarketView:
        cutoff = ensure_aware(decision_time, "decision_time")
        idx = bisect.bisect_right(list(self.available_at), cutoff)
        return MarketView(panel=self, stop=idx, as_of=cutoff)

    # -- simulator-only accessors ----------------------------------------
    def row_starting_at(self, when: datetime) -> int:
        """Index of the bar starting exactly at ``when`` (execution bar)."""

        idx = bisect.bisect_left(self.starts, when)
        if idx >= len(self.starts) or self.starts[idx] != when:
            raise KeyError(f"no bar starts at {when.isoformat()}")
        return idx

    def execution_prices(self, when: datetime) -> np.ndarray:
        """Official-style execution price proxy: open of the bar starting at ``when``."""

        return self.open[self.row_starting_at(when)].copy()

    def close_at(self, when: datetime) -> np.ndarray:
        """Close of the bar ending exactly at ``when`` (e.g. 16:00 valuation)."""

        idx = bisect.bisect_left(self.ends, when)
        if idx >= len(self.ends) or self.ends[idx] != when:
            raise KeyError(f"no bar ends at {when.isoformat()}")
        return self.close[idx].copy()

    def trading_days(self) -> list[date]:
        return sorted({et_date(s) for s in self.starts})

    @property
    def bars_per_hour(self) -> float:
        return 60.0 / self.bar_minutes

    @property
    def bars_per_day(self) -> float:
        return TRADING_MINUTES_PER_DAY / self.bar_minutes


def _is_session_tail(bar: MarketBar, bar_minutes: int) -> bool:
    """Allow a shorter final bar ending at the close (e.g. 15:30-16:00 for 60-min bars)."""

    length = (bar.end - bar.start).total_seconds() / 60.0
    return 0 < length < bar_minutes


@dataclass(frozen=True)
class MarketView:
    """Read-only, decision-time slice of a panel (rows ``[0, stop)``)."""

    panel: MarketPanel
    stop: int
    as_of: datetime

    def __post_init__(self) -> None:
        if self.stop > 0 and self.panel.available_at[self.stop - 1] > self.as_of:
            raise LeakageViolation("MarketView contains a bar not yet available")

    @property
    def n_bars(self) -> int:
        return self.stop

    @property
    def close(self) -> np.ndarray:
        return self.panel.close[: self.stop]

    @property
    def open(self) -> np.ndarray:
        return self.panel.open[: self.stop]

    @property
    def volume(self) -> np.ndarray:
        return self.panel.volume[: self.stop]

    @property
    def ends(self) -> Sequence[datetime]:
        return self.panel.ends[: self.stop]

    @property
    def last_bar_end(self) -> datetime | None:
        return self.panel.ends[self.stop - 1] if self.stop else None

    def last_close(self) -> np.ndarray:
        """Latest visible close per symbol (forward-filled across missing bars)."""

        out = np.full(len(SYMBOLS), np.nan)
        closes = self.close
        for j in range(len(SYMBOLS)):
            col = closes[:, j]
            valid = np.flatnonzero(np.isfinite(col))
            if valid.size:
                out[j] = col[valid[-1]]
        return out

    def staleness(self) -> timedelta | None:
        end = self.last_bar_end
        return None if end is None else self.as_of - end

    def bars(self, hours: float) -> int:
        """Number of bars covering ``hours`` of *trading* time (>= 1)."""

        return max(1, int(round(hours * self.panel.bars_per_hour)))
