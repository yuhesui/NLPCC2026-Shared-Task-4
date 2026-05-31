"""Lightweight price-regime state used by HGF/MPC MVP agents."""

from __future__ import annotations

from typing import Any

from nlpcc.stage3_trade.schema import Stage3State


def classify_regime(momentum: float, volatility: float, drawdown: float) -> str:
    if drawdown > 0.12 or (volatility > 0.025 and momentum < 0):
        return "risk_off"
    if momentum > 0.01 and volatility < 0.025:
        return "risk_on"
    if abs(momentum) <= 0.003:
        return "neutral"
    return "transition"


def build_price_hmm_state(state: Stage3State) -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}
    counts: dict[str, int] = {}
    for fund_id, asset in state.assets.items():
        regime = classify_regime(asset.momentum, asset.volatility, asset.drawdown)
        counts[regime] = counts.get(regime, 0) + 1
        rows[fund_id] = {
            "regime": regime,
            "momentum": round(asset.momentum, 8),
            "volatility": round(asset.volatility, 8),
            "drawdown": round(asset.drawdown, 8),
        }
    dominant = max(counts, key=counts.get) if counts else "unknown"
    return {
        "status": "available_mvp",
        "component": "price_hmm_state",
        "dominant_regime": dominant,
        "regime_counts": counts,
        "asset_regimes": rows,
    }
