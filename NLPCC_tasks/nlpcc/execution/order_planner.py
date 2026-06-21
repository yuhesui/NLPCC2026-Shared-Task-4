"""Target-weight to official-trade order planner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from nlpcc.execution.trade_validator import TradeValidationResult, validate_official_trades
from nlpcc.stage3_trade.models.cash_feasibility import estimate_current_weights, plan_rebalance_trades


@dataclass(frozen=True)
class OrderPlannerConfig:
    rebalance_threshold: float = 0.01
    cash_reserve: float = 0.03
    max_weight: float = 0.35
    max_turnover: float = 0.25
    min_trade_amount: float = 1e-6
    min_sell_percentage: float = 1e-6

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any] | None) -> "OrderPlannerConfig":
        if not values:
            return cls()
        data = dict(values)
        if "constraints" in data and isinstance(data["constraints"], Mapping):
            merged = dict(data["constraints"])
            for key in ("rebalance_threshold", "cash_reserve", "max_weight", "max_turnover"):
                if key in data:
                    merged[key] = data[key]
            data = merged
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})


@dataclass(frozen=True)
class OrderPlan:
    trades: tuple[dict[str, float | str], ...]
    rejected_trades: tuple[dict[str, Any], ...]
    diagnostics: dict[str, Any]

    @property
    def ok(self) -> bool:
        return not self.rejected_trades


def plan_orders_from_target_weights(
    target_weights: Mapping[str, float],
    *,
    current_portfolio: Mapping[str, Any],
    current_open_by_fund: Mapping[str, float],
    fund_pool: tuple[str, ...],
    config: OrderPlannerConfig | Mapping[str, Any] | None = None,
) -> OrderPlan:
    resolved = config if isinstance(config, OrderPlannerConfig) else OrderPlannerConfig.from_mapping(config)
    current_weights, decision_cash = estimate_current_weights(dict(current_portfolio), dict(current_open_by_fund))
    raw_trades = plan_rebalance_trades(
        dict(target_weights),
        dict(current_portfolio),
        dict(current_open_by_fund),
        rebalance_threshold=resolved.rebalance_threshold,
        cash_reserve=resolved.cash_reserve,
        max_weight=resolved.max_weight,
        max_turnover=resolved.max_turnover,
        min_trade_amount=resolved.min_trade_amount,
        min_sell_percentage=resolved.min_sell_percentage,
    )
    validation: TradeValidationResult = validate_official_trades(
        raw_trades,
        current_portfolio=dict(current_portfolio),
        fund_pool=fund_pool,
        available_cash=decision_cash,
        min_amount=resolved.min_trade_amount,
    )
    diagnostics = {
        "planner_config": asdict(resolved),
        "current_weights": current_weights,
        "target_weight_sum": sum(max(0.0, float(value)) for value in target_weights.values()),
        "raw_trade_count": len(raw_trades),
        "valid_trade_count": len(validation.valid_trades),
        "rejected_trade_count": len(validation.rejected_trades),
        "validation_issues": list(validation.issues),
        "buy_budget_uses_decision_cash_only": True,
    }
    return OrderPlan(validation.valid_trades, validation.rejected_trades, diagnostics)
