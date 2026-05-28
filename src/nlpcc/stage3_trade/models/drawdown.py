"""Drawdown features."""

from __future__ import annotations


def max_drawdown_from_prices(closes: list[float] | tuple[float, ...], window: int | None = None) -> float:
    values = [float(value) for value in closes if value is not None and float(value) > 0]
    if window is not None and window > 0:
        values = values[-window:]
    if not values:
        return 0.0
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak <= 0:
            continue
        worst = min(worst, (value / peak) - 1.0)
    return abs(worst)


def drawdown_penalty(drawdown: float, cap: float = 0.5) -> float:
    if cap <= 0:
        return 0.0
    return max(0.0, min(1.0, drawdown / cap))
