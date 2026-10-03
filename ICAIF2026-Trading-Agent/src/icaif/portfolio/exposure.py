"""Dynamic gross exposure  g_t = sum_i w_i,  0 <= g_t <= 1.

AlphaAllocator ran at a fixed ~97% invested weight. Here gross exposure is an
explicit model output composed from independent components; the final value
is the minimum of active components (each is a ceiling), clipped to
``[min_gross, max_gross]``. Every component's value is reported for traces.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from icaif.features.regime import RegimeState


@dataclass(frozen=True)
class ExposureDecision:
    gross: float
    components: dict[str, float] = field(default_factory=dict)


def vol_target_gross(predicted_vol_ann: float, target_vol_ann: float) -> float:
    if not np.isfinite(predicted_vol_ann) or predicted_vol_ann <= 0:
        return 1.0
    return float(min(1.0, target_vol_ann / predicted_vol_ann))


def regime_gross(regime: RegimeState, *, trend_floor: float, breadth_floor: float, risk_off_gross: float,
                 high_vol_percentile: float = 1.01, high_vol_gross: float = 1.0) -> float:
    g = 1.0
    if regime.market_trend < trend_floor and regime.breadth < breadth_floor:
        g = min(g, risk_off_gross)
    if regime.vol_percentile >= high_vol_percentile:
        g = min(g, high_vol_gross)
    return g


def drawdown_gross(nav_drawdown: float, *, start: float, full: float, min_gross: float) -> float:
    """Linear de-risking from 1 at ``start`` drawdown to ``min_gross`` at ``full``."""

    if nav_drawdown <= start:
        return 1.0
    if nav_drawdown >= full:
        return min_gross
    frac = (nav_drawdown - start) / (full - start)
    return float(1.0 - frac * (1.0 - min_gross))


def decide_gross(
    config: Mapping[str, Any],
    *,
    predicted_vol_ann: float | None = None,
    regime: RegimeState | None = None,
    nav_drawdown: float = 0.0,
) -> ExposureDecision:
    """Compose the configured components. ``config`` example::

        {"base": 1.0, "min_gross": 0.0, "max_gross": 1.0,
         "vol_target": {"target_vol_ann": 0.15},
         "regime": {"trend_floor": -0.02, "breadth_floor": 0.4, "risk_off_gross": 0.5},
         "drawdown": {"start": 0.03, "full": 0.10, "min_gross": 0.3}}
    """

    comps: dict[str, float] = {"base": float(config.get("base", 1.0))}
    if "vol_target" in config:
        if predicted_vol_ann is None:
            raise ValueError("vol_target exposure needs predicted_vol_ann")
        comps["vol_target"] = vol_target_gross(predicted_vol_ann, float(config["vol_target"]["target_vol_ann"]))
    if "regime" in config:
        if regime is None:
            raise ValueError("regime exposure needs a RegimeState")
        comps["regime"] = regime_gross(regime, **config["regime"])
    if "drawdown" in config:
        comps["drawdown"] = drawdown_gross(nav_drawdown, **config["drawdown"])
    lo = float(config.get("min_gross", 0.0))
    hi = float(config.get("max_gross", 1.0))
    if not 0.0 <= lo <= hi <= 1.0:
        raise ValueError("exposure bounds must satisfy 0 <= min <= max <= 1")
    gross = float(np.clip(min(comps.values()), lo, hi))
    return ExposureDecision(gross, comps)
