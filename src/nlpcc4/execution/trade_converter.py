"""Target-weight to official-trade conversion.

Strategies must return target weights first. This module is the only intended
place for converting those targets into official buy/sell API payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from nlpcc4.execution.target_weights import validate_target_weights


@dataclass(frozen=True)
class TradeConversionRequest:
    """Inputs required to convert target weights into official trade actions."""

    target_weights: Mapping[str, float]
    current_weights: Mapping[str, float]
    portfolio_value: float
    cash: float
    current_values: Mapping[str, float] = field(default_factory=dict)
    no_trade_band: float = 0.0
    max_turnover: float | None = None
    cash_buffer: float = 0.0
    diagnostics: Mapping[str, object] = field(default_factory=dict)


def convert_target_weights_to_trades(request: TradeConversionRequest) -> list[dict]:
    """Convert target weights to official trade payloads.

    Official semantics inspected in Phase 1a:
    - buy payload: ``{"fund_id": code, "action": "buy", "amount": cash_amount}``
    - sell payload: ``{"fund_id": code, "action": "sell", "percentage": holding_fraction}``
    - the official engine executes buys before sells, so buys here are limited
      to already available cash and never rely on sale proceeds.
    """
    validate_target_weights(request.target_weights)
    if request.portfolio_value <= 0:
        return []

    keys = sorted(set(request.target_weights) | set(request.current_weights))
    band = max(0.0, float(request.no_trade_band or 0.0))
    trades: list[dict] = []
    buy_needs: dict[str, float] = {}

    for asset in keys:
        current_weight = float(request.current_weights.get(asset, 0.0))
        target_weight = float(request.target_weights.get(asset, 0.0))
        if abs(target_weight - current_weight) < band:
            continue
        current_value = float(request.current_values.get(asset, current_weight * request.portfolio_value))
        desired_value = target_weight * request.portfolio_value
        delta = desired_value - current_value
        if delta < -1e-8 and current_value > 1e-8:
            percentage = min(1.0, max(0.0, -delta / current_value))
            if percentage > 1e-6:
                trades.append({"fund_id": asset, "action": "sell", "percentage": percentage})
        elif delta > 1e-8:
            buy_needs[asset] = delta

    available_cash = max(0.0, float(request.cash) - float(request.cash_buffer) * request.portfolio_value)
    total_buy_need = sum(buy_needs.values())
    scale = 1.0 if total_buy_need <= available_cash or total_buy_need <= 0 else available_cash / total_buy_need
    for asset, amount in buy_needs.items():
        scaled_amount = amount * scale
        if scaled_amount > 1e-6:
            trades.append({"fund_id": asset, "action": "buy", "amount": scaled_amount})

    return trades
