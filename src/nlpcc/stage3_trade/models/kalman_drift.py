"""Kalman-smoothed drift estimates from past complete returns."""

from __future__ import annotations

from typing import Any

from nlpcc.stage3_trade.schema import Stage3State


def kalman_drift_estimate(
    returns: tuple[float, ...],
    *,
    process_variance: float = 1e-5,
    observation_variance: float = 2e-4,
) -> dict[str, float]:
    if not returns:
        return {"drift": 0.0, "variance": observation_variance, "confidence": 0.0}
    estimate = 0.0
    variance = 1.0
    for value in returns:
        variance += process_variance
        gain = variance / (variance + observation_variance)
        estimate = estimate + gain * (float(value) - estimate)
        variance = (1.0 - gain) * variance
    confidence = max(0.0, min(1.0, 1.0 / (1.0 + 1000.0 * variance)))
    return {"drift": round(estimate, 8), "variance": round(variance, 10), "confidence": round(confidence, 8)}


def build_kalman_drift_state(state: Stage3State) -> dict[str, Any]:
    assets = {
        fund_id: kalman_drift_estimate(asset.prior_returns)
        for fund_id, asset in state.assets.items()
    }
    return {
        "status": "available_mvp",
        "component": "kalman_drift_state",
        "assets": assets,
    }
