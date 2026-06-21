"""Market breadth features."""

from __future__ import annotations


def breadth_score(returns: list[float] | tuple[float, ...], window: int = 20) -> float:
    values = tuple(float(value) for value in returns)
    if window > 0:
        values = values[-window:]
    if not values:
        return 0.5
    positives = sum(1 for value in values if value > 0)
    return positives / len(values)


def cross_sectional_breadth(momentum_by_fund: dict[str, float]) -> float:
    if not momentum_by_fund:
        return 0.5
    positives = sum(1 for value in momentum_by_fund.values() if value > 0)
    return positives / len(momentum_by_fund)
