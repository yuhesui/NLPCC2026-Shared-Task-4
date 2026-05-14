"""Turnover metric utilities."""

from __future__ import annotations

from statistics import mean


def average_turnover(turnover_series: list[float]) -> float:
    """Return average turnover for a precomputed turnover series."""
    return mean(turnover_series) if turnover_series else 0.0


def total_turnover(turnover_series: list[float]) -> float:
    """Return total one-way turnover."""
    return sum(turnover_series)
