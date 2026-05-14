"""Equal-weight baseline component for S0."""

from __future__ import annotations

from typing import Sequence

from nlpcc4.execution.constraints import project_long_only


def equal_weight_targets(
    fund_pool: Sequence[str],
    *,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
) -> dict[str, float]:
    """Return equal target weights with optional cash buffer and cap."""
    if not fund_pool:
        raise ValueError("fund_pool must not be empty")
    raw = {asset: 1.0 for asset in fund_pool}
    return project_long_only(raw, universe=fund_pool, max_weight=max_weight, cash_buffer=cash_buffer)
