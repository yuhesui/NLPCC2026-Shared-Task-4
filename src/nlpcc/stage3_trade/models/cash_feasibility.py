"""Cash-aware target-weight to official-trade conversion.

The official server reports holdings as monetary holding value. Older local
tools in this repo keep holdings as share-like quantities. The helpers below
support both forms explicitly so the execution path does not silently multiply
official holding value by price.
"""

from __future__ import annotations

from typing import Any


def holding_shares(holding: Any) -> float:
    """Return share-like quantity from a local holding object.

    Official holdings that expose ``value`` or ``market_value`` are not
    share-like and therefore return zero here. Use :func:`holding_value` when
    the intent is portfolio valuation.
    """

    if isinstance(holding, dict):
        if "value" in holding or "market_value" in holding:
            return 0.0
        return float(holding.get("shares", holding.get("quantity", holding.get("amount", 0.0))) or 0.0)
    return float(holding or 0.0)


def holding_value(holding: Any, current_price: float | None = None) -> float:
    """Return current monetary value for either official or local holdings."""

    if isinstance(holding, dict):
        if "value" in holding:
            return max(0.0, float(holding.get("value") or 0.0))
        if "market_value" in holding:
            return max(0.0, float(holding.get("market_value") or 0.0))
        shares = holding_shares(holding)
    else:
        shares = holding_shares(holding)
    price = float(current_price or 0.0)
    if shares <= 0 or price <= 0:
        return 0.0
    return shares * price


def estimate_current_weights(
    current_portfolio: dict[str, Any],
    current_open_by_fund: dict[str, float],
) -> tuple[dict[str, float], float]:
    cash = float(current_portfolio.get("cash", current_portfolio.get("capital", 0.0)) or 0.0)
    holdings = current_portfolio.get("holdings", {}) or {}
    values: dict[str, float] = {}
    for fund_id, holding in holdings.items():
        price = float(current_open_by_fund.get(fund_id, 0.0) or 0.0)
        value = holding_value(holding, price)
        if value > 0:
            values[fund_id] = value
    reported_total = current_portfolio.get("total_value")
    total_value = float(reported_total) if reported_total not in (None, "") else cash + sum(values.values())
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
    max_weight: float | None = None,
    max_turnover: float | None = None,
    min_trade_amount: float = 1e-6,
    min_sell_percentage: float = 1e-6,
) -> list[dict[str, float | str]]:
    """Create official-style sell-percentage and buy-cash trades.

    Buy amounts are capped by cash available at decision time. Planned same-day
    sales are not used to finance same-day buys.
    """

    current_weights, decision_cash = estimate_current_weights(current_portfolio, current_open_by_fund)
    holdings = current_portfolio.get("holdings", {}) or {}
    position_values = {
        fund_id: holding_value(holding, float(current_open_by_fund.get(fund_id, 0.0) or 0.0))
        for fund_id, holding in holdings.items()
    }
    reported_total = current_portfolio.get("total_value")
    total_value = float(reported_total) if reported_total not in (None, "") else decision_cash + sum(
        value for value in position_values.values() if value > 0
    )
    if total_value <= 0:
        total_value = decision_cash
    clean_targets = _prepare_target_weights(
        target_weights,
        current_weights,
        max_weight=max_weight,
        max_turnover=max_turnover,
    )

    sells: list[dict[str, float | str]] = []
    buy_needs: list[tuple[str, float]] = []
    for fund_id in sorted(set(current_weights) | set(clean_targets)):
        target = max(0.0, float(clean_targets.get(fund_id, 0.0)))
        current = max(0.0, float(current_weights.get(fund_id, 0.0)))
        diff = target - current
        if abs(diff) < rebalance_threshold:
            continue
        if diff < 0 and position_values.get(fund_id, 0.0) > 0:
            percentage = min(1.0, abs(diff) / current) if current > 0 else 1.0
            if percentage >= min_sell_percentage:
                sells.append({"fund_id": fund_id, "action": "sell", "percentage": round(percentage, 6)})
        elif diff > 0:
            buy_needs.append((fund_id, diff * total_value))

    buy_budget = max(0.0, decision_cash - (cash_reserve * total_value))
    total_needed = sum(amount for _, amount in buy_needs)
    scale = min(1.0, buy_budget / total_needed) if total_needed > 0 else 0.0
    buys = [
        {"fund_id": fund_id, "action": "buy", "amount": round(amount * scale, 6)}
        for fund_id, amount in buy_needs
        if amount * scale >= min_trade_amount
    ]
    return sells + buys


def _prepare_target_weights(
    target_weights: dict[str, float],
    current_weights: dict[str, float],
    *,
    max_weight: float | None,
    max_turnover: float | None,
) -> dict[str, float]:
    clean = {fund_id: max(0.0, float(weight)) for fund_id, weight in target_weights.items()}
    if max_weight is not None:
        cap = max(0.0, float(max_weight))
        clean = {fund_id: min(cap, weight) for fund_id, weight in clean.items()}
    if max_turnover is None:
        return clean
    assets = set(current_weights) | set(clean)
    turnover = 0.5 * sum(abs(clean.get(asset, 0.0) - current_weights.get(asset, 0.0)) for asset in assets)
    limit = max(0.0, float(max_turnover))
    if turnover <= limit or turnover <= 0:
        return clean
    blend = limit / turnover
    return {
        asset: current_weights.get(asset, 0.0) + blend * (clean.get(asset, 0.0) - current_weights.get(asset, 0.0))
        for asset in assets
    }
