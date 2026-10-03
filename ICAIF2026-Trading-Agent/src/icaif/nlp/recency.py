"""Event-specific temporal decay  w = exp(-Δt / τ_e).

AlphaAllocator used one fixed 2-day half-life (and silently returned 0.65 on
an unparseable timestamp). Here τ depends on the event type (configured in
``configs/news/event_priors.yaml``), Δt can be wall-clock or trading hours,
and a timestamp after the decision time raises instead of being clipped.
"""

from __future__ import annotations

import math
from datetime import datetime

from icaif.core.leakage_guard import LeakageViolation
from icaif.core.time import ET, ensure_aware


def trading_hours_between(start: datetime, end: datetime) -> float:
    """Regular-session hours (09:30-16:00 ET, Mon-Fri) in ``[start, end)``; no holiday calendar."""

    from datetime import time, timedelta

    s, e = ensure_aware(start).astimezone(ET), ensure_aware(end).astimezone(ET)
    if e <= s:
        return 0.0
    total = 0.0
    day = s.date()
    while day <= e.date():
        if day.weekday() < 5:
            o = datetime.combine(day, time(9, 30), tzinfo=ET)
            c = datetime.combine(day, time(16, 0), tzinfo=ET)
            lo, hi = max(o, s), min(c, e)
            if hi > lo:
                total += (hi - lo).total_seconds() / 3600.0
        day += timedelta(days=1)
    return total


def age_hours(available_at: datetime, decision_time: datetime, *, clock: str = "wall") -> float:
    a, d = ensure_aware(available_at), ensure_aware(decision_time)
    if a > d:
        raise LeakageViolation(f"item available at {a.isoformat()} is after decision time {d.isoformat()}")
    if clock == "wall":
        return (d - a).total_seconds() / 3600.0
    if clock == "trading":
        return trading_hours_between(a, d)
    raise ValueError(f"unknown clock {clock!r}")


def decay_weight(age: float, half_life_hours: float) -> float:
    if half_life_hours <= 0:
        raise ValueError("half_life_hours must be positive")
    return math.exp(-math.log(2.0) * age / half_life_hours)
