"""Realised volatility estimators on bar returns."""

from __future__ import annotations

import numpy as np

from icaif.data.market.panel import MarketView
from icaif.features.returns import bar_returns

VOL_FLOOR = 1e-6


def realized_vol(view: MarketView, lookback_bars: int) -> np.ndarray:
    """Per-bar sample std of returns over ``lookback_bars`` (NaN-aware, floored)."""

    rets = bar_returns(view, lookback_bars)
    if rets.shape[0] < 2:
        return np.full(view.close.shape[1], np.nan)
    with np.errstate(invalid="ignore"):
        vol = np.nanstd(rets, axis=0, ddof=1)
    return np.where(np.isfinite(vol), np.maximum(vol, VOL_FLOOR), np.nan)


def ewma_vol(view: MarketView, halflife_bars: float, lookback_bars: int) -> np.ndarray:
    rets = bar_returns(view, lookback_bars)
    if rets.shape[0] < 2:
        return np.full(view.close.shape[1], np.nan)
    decay = 0.5 ** (1.0 / halflife_bars)
    weights = decay ** np.arange(rets.shape[0] - 1, -1, -1, dtype=float)
    filled = np.where(np.isfinite(rets), rets, 0.0)
    mask = np.isfinite(rets).astype(float)
    wsum = (weights[:, None] * mask).sum(axis=0)
    var = (weights[:, None] * filled**2).sum(axis=0) / np.maximum(wsum, 1e-12)
    return np.maximum(np.sqrt(var), VOL_FLOOR)


def annualise_per_bar(vol_per_bar: np.ndarray | float, bars_per_day: float) -> np.ndarray | float:
    return vol_per_bar * np.sqrt(252.0 * bars_per_day)
