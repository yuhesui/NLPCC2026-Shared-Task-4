"""Sector trend-following baseline used by Track 2 S0/S1."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.data.features import momentum_return
from nlpcc4.execution.constraints import project_long_only


def sector_trend_targets(
    historical_prices: Mapping[str, Sequence[Mapping]],
    *,
    fund_pool: Sequence[str],
    top_k: int = 5,
    momentum_window: int = 20,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
) -> dict[str, float]:
    """Allocate to top-k positive sector trends."""
    scores = {asset: momentum_return(historical_prices.get(asset, ()), momentum_window) for asset in fund_pool}
    selected = sorted(scores, key=scores.get, reverse=True)[: max(1, min(top_k, len(fund_pool)))]
    raw = {asset: max(0.0, scores[asset]) if asset in selected else 0.0 for asset in fund_pool}
    if sum(raw.values()) <= 0:
        raw = {asset: 1.0 if asset in selected else 0.0 for asset in fund_pool}
    return project_long_only(raw, universe=fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
