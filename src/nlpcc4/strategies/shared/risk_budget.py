"""Risk-budgeting utilities for S1/S3."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.data.features import trailing_volatility
from nlpcc4.execution.constraints import project_long_only


def allocate_risk_budget(
    scores: Mapping[str, float],
    historical_prices: Mapping[str, Sequence[Mapping]],
    *,
    volatility_window: int = 20,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Convert positive scores into inverse-vol/risk-budget weights."""
    raw: dict[str, float] = {}
    for asset in (universe or tuple(scores.keys())):
        vol = trailing_volatility(historical_prices.get(asset, ()), window=volatility_window)
        raw[asset] = max(0.0, float(scores.get(asset, 0.0))) / max(vol, 1e-4)
    if sum(raw.values()) <= 0:
        raw = {asset: 1.0 for asset in (universe or tuple(scores.keys()))}
    return project_long_only(raw, universe=universe, max_weight=max_weight, cash_buffer=cash_buffer)
