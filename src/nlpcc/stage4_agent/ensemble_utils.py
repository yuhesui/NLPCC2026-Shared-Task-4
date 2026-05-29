"""Shared utilities for conservative Stage 4 ensembles."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from nlpcc.core.fund_universe import TrackName
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.position_sizing import estimate_current_weights, target_weights_to_trades
from nlpcc.portfolio.target_weights import project_long_only_capped_weights
from nlpcc.portfolio.turnover_control import apply_turnover_limit


def current_open_by_fund(historical_prices: Mapping[str, list[dict[str, Any]]], fund_pool: tuple[str, ...]) -> dict[str, float]:
    prices: dict[str, float] = {}
    for fund_id in fund_pool:
        rows = historical_prices.get(fund_id, [])
        if not rows:
            continue
        value = rows[-1].get("open")
        if value not in (None, ""):
            prices[fund_id] = float(value)
    return prices


def blend_target_weights(
    weighted_targets: Mapping[str, tuple[float, Mapping[str, float]]],
    *,
    constraints: PortfolioConstraints,
    assets: tuple[str, ...],
) -> dict[str, float]:
    raw: dict[str, float] = {}
    for gate, weights in weighted_targets.values():
        for asset, weight in weights.items():
            if asset in assets:
                raw[asset] = raw.get(asset, 0.0) + float(gate) * float(weight)
    if not raw:
        return {}
    return project_long_only_capped_weights(
        raw,
        assets,
        max_weight=constraints.max_weight,
        total=constraints.invested_weight,
    )


def build_weight_decision(
    *,
    agent_name: str,
    track: TrackName,
    fund_pool: tuple[str, ...],
    historical_prices: dict[str, list[dict[str, Any]]],
    current_portfolio: dict[str, Any],
    constraints: PortfolioConstraints,
    raw_target_weights: Mapping[str, float],
    reasoning: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    assets = tuple(asset for asset in fund_pool if asset in raw_target_weights) or fund_pool
    projected = project_long_only_capped_weights(
        raw_target_weights,
        assets,
        max_weight=constraints.max_weight,
        total=constraints.invested_weight,
    )
    open_prices = current_open_by_fund(historical_prices, fund_pool)
    current_weights, _ = estimate_current_weights(current_portfolio, open_prices)
    target_weights = apply_turnover_limit(projected, current_weights, constraints)
    trades = target_weights_to_trades(
        target_weights,
        current_portfolio,
        open_prices,
        rebalance_threshold=constraints.rebalance_threshold,
        cash_reserve=constraints.cash_reserve,
    )
    merged_metadata = {
        "agent": agent_name,
        "track": track,
        "fallback_used": False,
        "current_day_fields_used": ["open"],
        "forbidden_current_fields_used": [],
    }
    merged_metadata.update(metadata)
    return {
        "trades": trades,
        "target_weights": target_weights,
        "reasoning": reasoning,
        "metadata": merged_metadata,
    }
