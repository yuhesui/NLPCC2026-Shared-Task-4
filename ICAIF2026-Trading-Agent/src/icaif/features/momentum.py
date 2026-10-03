"""Momentum / trend signals over multiple intraday and multi-day horizons."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from icaif.data.market.panel import MarketView
from icaif.features.cross_sectional import nan_to_neutral, zscore
from icaif.features.returns import HORIZON_HOURS, horizon_return
from icaif.features.volatility import realized_vol


def momentum(view: MarketView, horizon: str, *, skip_hours: float = 0.0) -> np.ndarray:
    """Return over ``horizon`` optionally skipping the most recent ``skip_hours``
    (short-term reversal guard)."""

    hours = HORIZON_HOURS[horizon]
    if skip_hours <= 0:
        return horizon_return(view, hours)
    k_total, k_skip = view.bars(hours + skip_hours), view.bars(skip_hours)
    close = view.close
    if close.shape[0] <= k_total:
        return np.full(close.shape[1], np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        return close[-1 - k_skip] / close[-1 - k_total] - 1.0


def vol_scaled_momentum(view: MarketView, horizon: str, *, vol_lookback_hours: float = 32.5) -> np.ndarray:
    """Momentum divided by realised vol scaled to the horizon (a t-stat-like score)."""

    raw = momentum(view, horizon)
    k = view.bars(HORIZON_HOURS[horizon])
    vol = realized_vol(view, view.bars(vol_lookback_hours))
    with np.errstate(invalid="ignore", divide="ignore"):
        return raw / (vol * np.sqrt(k))


def multi_horizon_score(view: MarketView, weights: Mapping[str, float], *, vol_scaled: bool = True) -> np.ndarray:
    """Weighted sum of cross-sectionally z-scored momentum across horizons.

    Missing horizons (insufficient history) contribute 0 and their weight is
    renormalised away, so short histories degrade gracefully and explicitly.
    """

    total = np.zeros(view.close.shape[1])
    used = 0.0
    for horizon, w in weights.items():
        sig = vol_scaled_momentum(view, horizon) if vol_scaled else momentum(view, horizon)
        if np.isfinite(sig).sum() < 2:
            continue
        total += w * nan_to_neutral(zscore(sig))
        used += abs(w)
    return total / used if used > 0 else total


def trend_strength(view: MarketView, fast_hours: float = 6.5, slow_hours: float = 32.5) -> np.ndarray:
    """(fast SMA / slow SMA - 1) per asset."""

    close = view.close
    kf, ks = view.bars(fast_hours), view.bars(slow_hours)
    if close.shape[0] < ks:
        return np.full(close.shape[1], np.nan)
    with np.errstate(invalid="ignore"):
        return np.nanmean(close[-kf:], axis=0) / np.nanmean(close[-ks:], axis=0) - 1.0
