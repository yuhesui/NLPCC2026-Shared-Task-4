"""Validation for official buy-amount / sell-percentage trade payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from nlpcc.portfolio.position_sizing import holding_value


@dataclass(frozen=True)
class TradeValidationResult:
    valid_trades: tuple[dict[str, float | str], ...]
    rejected_trades: tuple[dict[str, Any], ...]
    issues: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


def validate_official_trades(
    trades: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    current_portfolio: Mapping[str, Any] | None = None,
    fund_pool: tuple[str, ...] | None = None,
    available_cash: float | None = None,
    min_amount: float = 1e-6,
) -> TradeValidationResult:
    pool = set(fund_pool or ())
    cash_limit = float(
        available_cash
        if available_cash is not None
        else (current_portfolio or {}).get("cash", (current_portfolio or {}).get("capital", 0.0))
        or 0.0
    )
    holdings = dict((current_portfolio or {}).get("holdings", {}) or {})
    cumulative_buys = 0.0
    valid: list[dict[str, float | str]] = []
    rejected: list[dict[str, Any]] = []
    issues: list[str] = []

    for index, trade in enumerate(trades):
        reason = _trade_issue(trade, pool, holdings, min_amount)
        if reason is None and trade.get("action") == "buy":
            amount = float(trade.get("amount", 0.0) or 0.0)
            if cumulative_buys + amount > cash_limit + 1e-6:
                reason = "buy_cash_overspend"
            else:
                cumulative_buys += amount
        if reason:
            issues.append(f"{index}:{reason}")
            rejected.append({"index": index, "reason": reason, "trade": dict(trade)})
            continue
        cleaned: dict[str, float | str] = {"fund_id": str(trade["fund_id"]), "action": str(trade["action"])}
        if trade["action"] == "buy":
            cleaned["amount"] = round(float(trade["amount"]), 6)
        else:
            cleaned["percentage"] = round(float(trade["percentage"]), 6)
        valid.append(cleaned)
    return TradeValidationResult(tuple(valid), tuple(rejected), tuple(issues))


def _trade_issue(
    trade: Mapping[str, Any],
    fund_pool: set[str],
    holdings: Mapping[str, Any],
    min_amount: float,
) -> str | None:
    fund_id = trade.get("fund_id")
    if not fund_id or (fund_pool and fund_id not in fund_pool):
        return "invalid_fund_id"
    action = trade.get("action")
    if action == "buy":
        amount = trade.get("amount")
        if amount is None or trade.get("percentage") is not None:
            return "invalid_buy_fields"
        if float(amount or 0.0) < min_amount:
            return "invalid_buy_amount"
        return None
    if action == "sell":
        percentage = trade.get("percentage")
        if percentage is None or trade.get("amount") is not None:
            return "invalid_sell_fields"
        pct = float(percentage or 0.0)
        if pct <= 0 or pct > 1:
            return "invalid_sell_percentage"
        if fund_id not in holdings or holding_value(holdings[fund_id]) <= 0:
            return "sell_without_holding"
        return None
    return "invalid_action"
