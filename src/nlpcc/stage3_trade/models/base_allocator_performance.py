"""Base allocator performance-state MVP for ARMOR-OMD."""

from __future__ import annotations

from typing import Any, Mapping

from nlpcc.stage3_trade.schema import Stage3State


def build_base_allocator_performance_state(
    state: Stage3State,
    base_allocations: Mapping[str, Mapping[str, float]],
) -> dict[str, Any]:
    """Score base allocators using only prior-return estimates in Stage 3."""

    recent_return = {
        fund_id: (asset.prior_returns[-1] if asset.prior_returns else 0.0)
        for fund_id, asset in state.assets.items()
    }
    scores: dict[str, float] = {}
    risk: dict[str, float] = {}
    for name, weights in base_allocations.items():
        expected = sum(float(weights.get(fund_id, 0.0)) * recent_return.get(fund_id, 0.0) for fund_id in state.fund_pool)
        vol_penalty = sum(
            float(weights.get(fund_id, 0.0)) * state.assets[fund_id].volatility
            for fund_id in state.assets
        )
        scores[name] = round(expected - 0.25 * vol_penalty, 8)
        risk[name] = round(vol_penalty, 8)
    return {
        "status": "available_mvp",
        "component": "base_allocator_performance",
        "scores": scores,
        "risk": risk,
    }
