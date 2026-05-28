"""Cash-aware target-weight to official-trade conversion."""

from __future__ import annotations

from typing import Any


def holding_shares(holding: Any) -> float:
    if isinstance(holding, dict):
        return float(holding.get("shares", holding.get("quantity", holding.get("amount", 0.0))) or 0.0)
    return float(holding or 0.0)


def estimate_current_weights(
    current_portfolio: dict[str, Any],
    current_open_by_fund: dict[str, float],
) -> tuple[dict[str, float], float]:
    cash = float(current_portfolio.get("cash", current_portfolio.get("capital", 0.0)) or 0.0)
    holdings = current_portfolio.get("holdings", {}) or {}
    values: dict[str, float] = {}
    for fund_id, holding in holdings.items():
        shares = holding_shares(holding)
        price = float(current_open_by_fund.get(fund_id, 0.0) or 0.0)
        if shares > 0 and price > 0:
            values[fund_id] = shares * price
    total_value = cash + sum(values.values())
    if total_value <= 0:
        return {}, cash
    return {fund_id: value / total_value for fund_id, value in values.items()}, cash


def plan_rebalance_trades(
    target_weights: dict[str, float],
    current_portfolio: dict[str, Any],
    current_open_by_fund: dict[str, float],
    *,
    rebalance_threshold: float = 0.01,
    cash_reserve: float = 0.02,
) -> list[dict[str, float | str]]:
    """Create official-style sell-percentage and buy-cash trades.

    Buy amounts are capped by cash available at decision time. Planned same-day
    sales are not used to finance same-day buys.
    """

    current_weights, decision_cash = estimate_current_weights(current_portfolio, current_open_by_fund)
    holdings = current_portfolio.get("holdings", {}) or {}
    position_values = {
        fund_id: holding_shares(holding) * float(current_open_by_fund.get(fund_id, 0.0) or 0.0)
        for fund_id, holding in holdings.items()
    }
    total_value = decision_cash + sum(value for value in position_values.values() if value > 0)
    if total_value <= 0:
        total_value = decision_cash

    sells: list[dict[str, float | str]] = []
    buy_needs: list[tuple[str, float]] = []
    for fund_id in sorted(set(current_weights) | set(target_weights)):
        target = max(0.0, float(target_weights.get(fund_id, 0.0)))
        current = max(0.0, float(current_weights.get(fund_id, 0.0)))
        diff = target - current
        if abs(diff) < rebalance_threshold:
            continue
        if diff < 0 and position_values.get(fund_id, 0.0) > 0:
            percentage = min(1.0, abs(diff) / current) if current > 0 else 1.0
            if percentage > 0:
                sells.append({"fund_id": fund_id, "action": "sell", "percentage": round(percentage, 6)})
        elif diff > 0:
            buy_needs.append((fund_id, diff * total_value))

    buy_budget = max(0.0, decision_cash - (cash_reserve * total_value))
    total_needed = sum(amount for _, amount in buy_needs)
    scale = min(1.0, buy_budget / total_needed) if total_needed > 0 else 0.0
    buys = [
        {"fund_id": fund_id, "action": "buy", "amount": round(amount * scale, 6)}
        for fund_id, amount in buy_needs
        if amount * scale > 0
    ]
    return sells + buys
