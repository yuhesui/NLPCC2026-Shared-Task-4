"""Synthetic metric stress transforms."""

from __future__ import annotations

from nlpcc.news_overlay.synthetic.scenarios import SyntheticScenario


def apply_synthetic_stress(metric: dict[str, float], scenario: SyntheticScenario, *, overlay_active: bool) -> dict[str, float]:
    """Apply bounded research-only stress to a metric row."""

    overlay_factor = 1.0 if overlay_active else 0.25
    return {
        "return": round(metric["return"] + scenario.sharpe_shift * 0.03 * overlay_factor, 6),
        "sharpe": round(metric["sharpe"] + scenario.sharpe_shift * overlay_factor, 6),
        "max_drawdown": round(metric["max_drawdown"] + max(0.0, -scenario.sharpe_shift) * 0.01 + scenario.price_noise, 6),
        "turnover": round(metric["turnover"] * scenario.turnover_multiplier, 6),
    }
