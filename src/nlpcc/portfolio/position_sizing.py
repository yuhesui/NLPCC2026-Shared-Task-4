"""Position-sizing bridge to official-style trades."""

from __future__ import annotations

from typing import Any

from nlpcc.stage3_trade.models.cash_feasibility import estimate_current_weights, holding_value, plan_rebalance_trades


def target_weights_to_trades(
    target_weights: dict[str, float],
    current_portfolio: dict[str, Any],
    current_open_by_fund: dict[str, float],
    *,
    rebalance_threshold: float,
    cash_reserve: float,
    max_weight: float | None = None,
    max_turnover: float | None = None,
) -> list[dict[str, float | str]]:
    return plan_rebalance_trades(
        target_weights,
        current_portfolio,
        current_open_by_fund,
        rebalance_threshold=rebalance_threshold,
        cash_reserve=cash_reserve,
        max_weight=max_weight,
        max_turnover=max_turnover,
    )


__all__ = ["estimate_current_weights", "holding_value", "target_weights_to_trades"]
