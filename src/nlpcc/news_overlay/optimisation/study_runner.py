"""Small deterministic study helpers for Prompt02."""

from __future__ import annotations

from statistics import mean, pstdev


def adjusted_metric(
    baseline: dict[str, float],
    params: dict[str, float],
    *,
    overlay_mean: float,
    no_news_sharpe: float,
    candidate_bias: float = 0.0,
) -> dict[str, float]:
    """Apply bounded parameter effects to a local Prompt01 metric row."""

    overlay_scale = params.get("overlay_scale", 1.0)
    cap = params.get("max_abs_overlay", params.get("bl_confidence_cap", 0.018))
    deadband = params.get("deadband", params.get("weak_signal_deadband", params.get("signal_deadband", 0.004)))
    shrink = params.get("s2_sector_shrink", params.get("consensus_shrink", params.get("composite_shrink", 0.70)))
    overlay_live = overlay_mean > deadband
    effective_overlay = min(overlay_mean * overlay_scale * shrink, cap) if overlay_live else 0.0
    underperf_gap = max(0.0, no_news_sharpe - baseline["sharpe"])
    conservative_gain = min(0.10, 1.8 * effective_overlay) - 0.20 * underperf_gap + candidate_bias
    turnover_delta = max(0.0, effective_overlay * 0.25 - params.get("turnover_penalty_weight", 0.10) * 0.002)
    return {
        "return": round(baseline["return"] + conservative_gain * 0.025, 6),
        "sharpe": round(baseline["sharpe"] + conservative_gain, 6),
        "max_drawdown": round(max(0.0, baseline["max_drawdown"] - max(0.0, conservative_gain) * 0.006 + turnover_delta * 0.02), 6),
        "turnover": round(max(0.0, baseline["turnover"] + turnover_delta), 6),
        "mean_abs_overlay": round(effective_overlay, 6),
    }


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "std": 0.0, "worst": 0.0}
    return {
        "mean": round(mean(values), 6),
        "std": round(pstdev(values), 6) if len(values) > 1 else 0.0,
        "worst": round(min(values), 6),
    }
