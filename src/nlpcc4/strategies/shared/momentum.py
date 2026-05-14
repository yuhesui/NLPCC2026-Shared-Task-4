"""Momentum signal components for S0/S1."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.data.features import multi_horizon_momentum
from nlpcc4.execution.constraints import project_long_only


def momentum_scores(
    historical_prices: Mapping[str, Sequence[Mapping]],
    windows: Sequence[int] = (20,),
) -> dict[str, float]:
    """Compute multi-horizon momentum scores from visible history."""
    return multi_horizon_momentum(historical_prices, windows)


def momentum_targets(
    historical_prices: Mapping[str, Sequence[Mapping]],
    *,
    windows: Sequence[int] = (20,),
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Allocate to positive-momentum assets with cash residual if all are weak."""
    scores = momentum_scores(historical_prices, windows)
    positive = {asset: max(0.0, score) for asset, score in scores.items()}
    if sum(positive.values()) <= 0:
        positive = {asset: 1.0 for asset in scores}
    return project_long_only(
        positive,
        universe=universe or tuple(historical_prices.keys()),
        max_weight=max_weight,
        cash_buffer=cash_buffer,
    )
