"""Persistence / previous-weight baseline."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.strategies.shared.equal_weight import equal_weight_targets
from nlpcc4.execution.constraints import project_long_only


def persistence_targets(
    previous_weights: Mapping[str, float],
    fund_pool: Sequence[str],
    *,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
) -> dict[str, float]:
    """Keep previous weights, falling back to equal weight when absent."""
    if not previous_weights or sum(previous_weights.values()) <= 1e-12:
        return equal_weight_targets(fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
    return project_long_only(previous_weights, universe=fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
