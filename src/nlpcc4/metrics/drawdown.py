"""Drawdown metric utilities."""

from __future__ import annotations


def drawdown_series(equity_curve: list[float]) -> list[float]:
    """Return drawdown for each equity-curve point."""
    if not equity_curve:
        return []
    peak = equity_curve[0]
    result: list[float] = []
    for value in equity_curve:
        peak = max(peak, value)
        result.append(0.0 if peak <= 0 else value / peak - 1.0)
    return result


def max_drawdown(equity_curve: list[float]) -> float:
    """Return maximum drawdown as a negative decimal."""
    values = drawdown_series(equity_curve)
    return min(values) if values else 0.0
