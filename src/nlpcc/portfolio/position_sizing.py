"""Position-sizing bridge to official-style trades."""

from __future__ import annotations

from typing import Any

from nlpcc.stage3_trade.models.cash_feasibility import estimate_current_weights, plan_rebalance_trades


def target_weights_to_trades(
    target_weights: dict[str, float],
    current_portfolio: dict[str, Any],
    current_open_by_fund: dict[str, float],
    *,
    rebalance_threshold: float,
    cash_reserve: float,
) -> list[dict[str, float | str]]:
    return plan_rebalance_trades(
        target_weights,
        current_portfolio,
        current_open_by_fund,
        rebalance_threshold=rebalance_threshold,
        cash_reserve=cash_reserve,
    )


__all__ = ["estimate_current_weights", "target_weights_to_trades"]
