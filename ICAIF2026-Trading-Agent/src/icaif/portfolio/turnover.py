"""Turnover control (first-class: it costs fees AND is a ranking metric).

ICAIF turnover for round k is N_k / B_k with N_k = buy + sell notional, i.e.
the **two-sided** L1 change ``sum|w_target - w_current|`` measured on pre-trade
NAV. (AlphaAllocator used one-way ``0.5 * L1``; do not mix the two.)

``w_current`` must be the *drifted* weights of the actual holdings at the
latest visible prices, not the previous target.

Controls, applied in this order by :class:`TurnoverController`:
1. minimum total change (skip the round entirely below a threshold);
2. per-asset no-trade band (keep current weight if |Δ| < band);
3. sparse changes (only the m largest |Δ| are executed);
4. per-round cap (blend toward current);
5. per-day budget (remaining daily allowance caps the round).
Hysteresis for top-k selection lives in ``models/alpha/selection.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import numpy as np

from icaif.core.constants import FEE_RATE


def l1_turnover(target: np.ndarray, current: np.ndarray) -> float:
    return float(np.abs(np.asarray(target) - np.asarray(current)).sum())


def expected_fee(target: np.ndarray, current: np.ndarray, nav: float, fee_rate: float = FEE_RATE) -> float:
    return fee_rate * l1_turnover(target, current) * nav


def no_trade_band(target: np.ndarray, current: np.ndarray, band: float) -> np.ndarray:
    out = np.asarray(target, dtype=float).copy()
    keep = np.abs(out - current) < band
    out[keep] = current[keep]
    return out


def sparse_changes(target: np.ndarray, current: np.ndarray, max_names: int) -> np.ndarray:
    delta = np.asarray(target, dtype=float) - current
    if max_names <= 0:
        return np.asarray(current, dtype=float).copy()
    if np.count_nonzero(delta) <= max_names:
        return np.asarray(target, dtype=float).copy()
    keep = np.argsort(-np.abs(delta), kind="mergesort")[:max_names]
    out = np.asarray(current, dtype=float).copy()
    out[keep] = target[keep]
    return out


def cap_turnover(target: np.ndarray, current: np.ndarray, max_turnover: float) -> tuple[np.ndarray, float]:
    """Blend toward ``current`` so that L1 change <= ``max_turnover``. Returns (w, blend)."""

    to = l1_turnover(target, current)
    if to <= max_turnover or to == 0:
        return np.asarray(target, dtype=float).copy(), 1.0
    blend = max(0.0, max_turnover / to)
    return current + blend * (np.asarray(target) - current), blend


@dataclass
class DailyTurnoverBudget:
    max_daily: float
    day: date | None = None
    used: float = 0.0

    def remaining(self, today: date) -> float:
        if self.day != today:
            return self.max_daily
        return max(0.0, self.max_daily - self.used)

    def consume(self, today: date, amount: float) -> None:
        if self.day != today:
            self.day, self.used = today, 0.0
        self.used += amount

    def as_dict(self) -> dict[str, Any]:
        return {"max_daily": self.max_daily, "day": self.day.isoformat() if self.day else None, "used": self.used}


@dataclass(frozen=True)
class TurnoverConfig:
    min_total_change: float = 0.0
    band: float = 0.0
    max_names: int | None = None
    max_round: float | None = None
    max_daily: float | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> TurnoverConfig:
        return cls(**(data or {}))


@dataclass
class TurnoverOutcome:
    weights: np.ndarray
    hold: bool
    steps: dict[str, float] = field(default_factory=dict)


class TurnoverController:
    def __init__(self, config: TurnoverConfig, budget: DailyTurnoverBudget | None = None) -> None:
        self.config = config
        self.budget = budget or (DailyTurnoverBudget(config.max_daily) if config.max_daily is not None else None)

    def apply(self, target: np.ndarray, current: np.ndarray, today: date) -> TurnoverOutcome:
        cfg = self.config
        steps: dict[str, float] = {"raw": l1_turnover(target, current)}
        if steps["raw"] < cfg.min_total_change:
            return TurnoverOutcome(np.asarray(current, dtype=float).copy(), True, steps)
        w = np.asarray(target, dtype=float)
        if cfg.band > 0:
            w = no_trade_band(w, current, cfg.band)
            steps["after_band"] = l1_turnover(w, current)
        if cfg.max_names is not None:
            w = sparse_changes(w, current, cfg.max_names)
            steps["after_sparse"] = l1_turnover(w, current)
        cap = np.inf
        if cfg.max_round is not None:
            cap = cfg.max_round
        if self.budget is not None:
            cap = min(cap, self.budget.remaining(today))
            steps["daily_remaining"] = self.budget.remaining(today)
        if np.isfinite(cap):
            w, blend = cap_turnover(w, current, cap)
            steps["blend"] = blend
        steps["final"] = l1_turnover(w, current)
        return TurnoverOutcome(w, steps["final"] == 0.0, steps)

    def commit(self, today: date, executed_turnover: float) -> None:
        """Record turnover that was actually submitted (call only after submit)."""

        if self.budget is not None:
            self.budget.consume(today, executed_turnover)
