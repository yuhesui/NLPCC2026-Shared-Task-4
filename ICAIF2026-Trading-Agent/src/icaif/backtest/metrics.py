"""Supplementary (non-ranking) diagnostics alongside the official metrics."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np


def concentration_hhi(w: np.ndarray) -> float:
    s = float(np.sum(w))
    if s <= 0:
        return 0.0
    p = np.asarray(w) / s
    return float(np.sum(p**2))


def summarize_rounds(rows: Sequence[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {}
    def col(key: str) -> np.ndarray:
        return np.array([float(r.get(key, 0.0) or 0.0) for r in rows])

    turnover = col("round_turnover")
    days: dict[str, float] = {}
    for r in rows:
        days[r["day"]] = days.get(r["day"], 0.0) + float(r.get("round_turnover", 0.0))
    return {
        "rounds": float(len(rows)),
        "rebalances": float(sum(1 for r in rows if r["action"] == "SUBMIT")),
        "holds": float(sum(1 for r in rows if r["action"] == "HOLD")),
        "fallback_rounds": float(sum(1 for r in rows if r.get("fallback"))),
        "mean_gross": float(col("gross_after").mean()),
        "min_gross": float(col("gross_after").min()),
        "mean_cash_weight": float(1.0 - col("gross_after").mean()),
        "mean_names": float(col("names").mean()),
        "mean_hhi": float(col("hhi").mean()),
        "mean_round_turnover": float(turnover.mean()),
        "max_round_turnover": float(turnover.max()),
        "mean_daily_turnover": float(np.mean(list(days.values()))),
        "max_daily_turnover": float(np.max(list(days.values()))),
        "total_fees": float(col("fee").sum()),
        "news_driven_turnover": float(col("news_driven_turnover").sum()),
        "price_driven_turnover": float(turnover.sum() - col("news_driven_turnover").sum()),
        "fee_funding_adjustments": float(sum(1 for r in rows if r.get("funding_scale", 1.0) < 1.0)),
    }
