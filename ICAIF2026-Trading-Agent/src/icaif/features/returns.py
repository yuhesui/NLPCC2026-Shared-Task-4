"""Bar returns from a point-in-time :class:`MarketView`.

All functions take a view (already cut at the decision time) and never look
past ``view.stop``. Missing bars propagate as NaN; consumers decide how to
treat them explicitly.
"""

from __future__ import annotations

import numpy as np

from icaif.data.market.panel import MarketView

# Horizons in trading hours. One US session is 6.5 trading hours.
HORIZON_HOURS: dict[str, float] = {"1h": 1.0, "2h": 2.0, "4h": 4.0, "1d": 6.5, "5d": 32.5, "20d": 130.0}


def bar_returns(view: MarketView, lookback_bars: int | None = None) -> np.ndarray:
    """Simple close-to-close returns, shape (T-1, N) or (lookback, N).

    The first bar of a session's return includes the overnight gap.
    """

    close = view.close
    if close.shape[0] < 2:
        return np.empty((0, close.shape[1]))
    if lookback_bars is not None:
        close = close[-(lookback_bars + 1):]
    with np.errstate(invalid="ignore", divide="ignore"):
        return close[1:] / close[:-1] - 1.0


def horizon_return(view: MarketView, hours: float) -> np.ndarray:
    """Return over the last ``hours`` of trading time ending at the latest visible bar.

    NaN where history is too short or prices are missing.
    """

    k = view.bars(hours)
    close = view.close
    if close.shape[0] <= k:
        return np.full(close.shape[1], np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        return close[-1] / close[-1 - k] - 1.0


def forward_returns(close: np.ndarray, start_idx: int, horizon_bars: int) -> np.ndarray:
    """Research/label helper on a FULL panel array (never on a decision view)."""

    end = start_idx + horizon_bars
    if end >= close.shape[0]:
        return np.full(close.shape[1], np.nan)
    return close[end] / close[start_idx] - 1.0
