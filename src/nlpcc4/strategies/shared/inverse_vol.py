"""Inverse-volatility weighting component for S0/S1."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.data.features import inverse_vol_scores
from nlpcc4.execution.constraints import project_long_only


def inverse_vol_targets(
    historical_prices: Mapping[str, Sequence[Mapping]],
    *,
    volatility_window: int = 20,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Compute inverse-volatility target weights from visible history."""
    scores = inverse_vol_scores(historical_prices, window=volatility_window)
    return project_long_only(
        scores,
        universe=universe or tuple(historical_prices.keys()),
        max_weight=max_weight,
        cash_buffer=cash_buffer,
    )
