"""Market regime descriptors used by dynamic gross exposure."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.data.market.panel import MarketView
from icaif.features.returns import bar_returns, horizon_return


@dataclass(frozen=True)
class RegimeState:
    market_trend: float  # equal-weight index return over trend horizon
    breadth: float  # fraction of assets with positive return over breadth horizon
    market_vol_per_bar: float  # realised vol of the equal-weight index
    vol_percentile: float  # current index vol vs its own trailing distribution [0,1]
    index_drawdown: float  # drawdown of the EW index from its trailing peak
    bars_available: int

    def as_dict(self) -> dict[str, float]:
        return self.__dict__.copy()


def equal_weight_index(view: MarketView) -> np.ndarray:
    rets = bar_returns(view)
    if rets.size == 0:
        return np.ones(1)
    ew = np.nanmean(np.where(np.isfinite(rets), rets, np.nan), axis=1)
    ew = np.where(np.isfinite(ew), ew, 0.0)
    return np.concatenate([[1.0], np.cumprod(1.0 + ew)])


def regime_state(view: MarketView, *, trend_hours: float = 32.5, breadth_hours: float = 32.5,
                 vol_hours: float = 13.0, vol_history_hours: float = 260.0) -> RegimeState:
    index = equal_weight_index(view)
    k_trend, k_vol, k_hist = view.bars(trend_hours), view.bars(vol_hours), view.bars(vol_history_hours)
    trend = float(index[-1] / index[-1 - k_trend] - 1.0) if index.size > k_trend else 0.0
    br = horizon_return(view, breadth_hours)
    breadth = float(np.mean(br[np.isfinite(br)] > 0)) if np.isfinite(br).any() else 0.5
    idx_rets = np.diff(index) / index[:-1]
    vol_now = float(np.std(idx_rets[-k_vol:], ddof=1)) if idx_rets.size > k_vol else float("nan")
    pct = 0.5
    if idx_rets.size > k_hist and np.isfinite(vol_now):
        windows = np.lib.stride_tricks.sliding_window_view(idx_rets[-k_hist:], k_vol)
        hist = windows.std(axis=1, ddof=1)
        pct = float(np.mean(hist <= vol_now))
    peak = np.max(index[-k_hist:]) if index.size else 1.0
    dd = float(1.0 - index[-1] / peak) if peak > 0 else 0.0
    return RegimeState(trend, breadth, vol_now, pct, dd, view.n_bars)
