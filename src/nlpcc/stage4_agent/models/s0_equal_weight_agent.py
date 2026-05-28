"""S0 equal-weight no-news baseline agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.stage3_trade.models.cash_feasibility import plan_rebalance_trades
from nlpcc.stage3_trade.models.equal_weight_state import cap_and_redistribute, equal_weight


def _current_open_by_fund(historical_prices: dict[str, list[dict[str, Any]]], fund_pool: tuple[str, ...]) -> dict[str, float]:
    prices: dict[str, float] = {}
    for fund_id in fund_pool:
        rows = historical_prices.get(fund_id, [])
        if not rows:
            continue
        value = rows[-1].get("open")
        if value not in (None, ""):
            prices[fund_id] = float(value)
    return prices


@dataclass(frozen=True)
class S0EqualWeightAgent:
    """Conservative equal-weight rebalancer.

    It only reads current-day opening prices for feasibility sizing. It does
    not inspect current-day close/high/low/return fields.
    """

    cash_reserve: float = 0.02
    max_weight: float = 0.35
    rebalance_threshold: float = 0.01

    def make_decision(
        self,
        *,
        track: TrackName = "macro",
        fund_pool: list[str] | tuple[str, ...] | None = None,
        historical_prices: dict[str, list[dict[str, Any]]] | None = None,
        news: list[dict[str, Any]] | None = None,
        current_portfolio: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del news
        historical_prices = historical_prices or {}
        current_portfolio = current_portfolio or {}
        pool = tuple(fund_pool or get_fund_pool(track))
        current_open = _current_open_by_fund(historical_prices, pool)
        available = tuple(fund_id for fund_id in pool if fund_id in current_open)
        invested_total = max(0.0, 1.0 - self.cash_reserve)
        target_weights = cap_and_redistribute(equal_weight(available, total=invested_total), self.max_weight, invested_total)
        trades = plan_rebalance_trades(
            target_weights,
            current_portfolio,
            current_open,
            rebalance_threshold=self.rebalance_threshold,
            cash_reserve=self.cash_reserve,
        )
        return {
            "trades": trades,
            "target_weights": target_weights,
            "reasoning": "S0 equal-weight no-news baseline.",
            "metadata": {
                "agent": "s0_equal_weight",
                "track": track,
                "available_funds": list(available),
                "current_day_fields_used": ["open"],
                "forbidden_current_fields_used": [],
            },
        }


def make_s0_decision(**kwargs: Any) -> dict[str, Any]:
    return S0EqualWeightAgent().make_decision(**kwargs)
