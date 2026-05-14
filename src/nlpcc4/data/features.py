"""Leakage-safe price feature builders."""

from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Mapping, Sequence


def visible_closed_rows(rows: Sequence[Mapping]) -> list[Mapping]:
    """Return only rows with a visible close, excluding current open-only rows."""
    return [row for row in rows if row.get("close") is not None]


def close_series(rows: Sequence[Mapping]) -> list[float]:
    """Return visible close prices as floats."""
    closes: list[float] = []
    for row in visible_closed_rows(rows):
        close = row.get("close")
        if close is not None:
            closes.append(float(close))
    return closes


def return_series(rows: Sequence[Mapping]) -> list[float]:
    """Return decimal returns from visible pct_change or close data."""
    returns: list[float] = []
    for row in visible_closed_rows(rows):
        pct = row.get("pct_change")
        if pct is not None:
            returns.append(float(pct) / 100.0)
    if returns:
        return returns
    closes = close_series(rows)
    return [closes[i] / closes[i - 1] - 1.0 for i in range(1, len(closes)) if closes[i - 1] > 0]


def trailing_volatility(rows: Sequence[Mapping], window: int = 20, floor: float = 1e-4) -> float:
    """Compute rolling daily volatility from visible returns."""
    values = return_series(rows)[-window:]
    if len(values) < 2:
        return floor
    vol = pstdev(values)
    return max(float(vol), floor)


def momentum_return(rows: Sequence[Mapping], window: int = 20) -> float:
    """Compute visible close-to-close momentum over a trailing window."""
    closes = close_series(rows)
    if len(closes) < 2:
        return 0.0
    use = min(window, len(closes) - 1)
    start = closes[-use - 1]
    end = closes[-1]
    if start <= 0:
        return 0.0
    return end / start - 1.0


def max_drawdown(rows: Sequence[Mapping], window: int = 60) -> float:
    """Compute trailing drawdown from visible closes."""
    closes = close_series(rows)[-window:]
    if not closes:
        return 0.0
    peak = closes[0]
    worst = 0.0
    for value in closes:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst


def zscore(values: Mapping[str, float]) -> dict[str, float]:
    """Cross-sectional z-score with stable zero handling."""
    if not values:
        return {}
    vals = list(values.values())
    mu = mean(vals)
    sigma = pstdev(vals)
    if sigma <= 1e-12:
        return {key: 0.0 for key in values}
    return {key: (float(value) - mu) / sigma for key, value in values.items()}


def multi_horizon_momentum(
    historical_prices: Mapping[str, Sequence[Mapping]], windows: Sequence[int]
) -> dict[str, float]:
    """Weighted average of visible momentum horizons."""
    if not windows:
        windows = (20,)
    scores: dict[str, float] = {}
    for asset, rows in historical_prices.items():
        horizon_scores = [momentum_return(rows, int(window)) for window in windows]
        scores[asset] = sum(horizon_scores) / len(horizon_scores)
    return scores


def inverse_vol_scores(
    historical_prices: Mapping[str, Sequence[Mapping]], window: int = 20
) -> dict[str, float]:
    """Return inverse volatility scores."""
    return {
        asset: 1.0 / trailing_volatility(rows, window=window)
        for asset, rows in historical_prices.items()
    }


def momentum_breadth(
    historical_prices: Mapping[str, Sequence[Mapping]], window: int = 20
) -> float:
    """Share of assets with positive trailing momentum."""
    if not historical_prices:
        return 0.0
    positives = sum(1 for rows in historical_prices.values() if momentum_return(rows, window) > 0)
    return positives / len(historical_prices)


def softmax_scores(scores: Mapping[str, float], temperature: float = 1.0) -> dict[str, float]:
    """Stable softmax for allocation scores."""
    if not scores:
        return {}
    temp = max(temperature, 1e-6)
    max_score = max(scores.values())
    exp_values = {asset: math.exp((score - max_score) / temp) for asset, score in scores.items()}
    total = sum(exp_values.values())
    if total <= 0:
        return {asset: 1.0 / len(scores) for asset in scores}
    return {asset: value / total for asset, value in exp_values.items()}
