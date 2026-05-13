"""Turnover-control stubs."""

from typing import Mapping


def estimate_turnover(current: Mapping[str, float], target: Mapping[str, float]) -> float:
    """Estimate one-way turnover between current and target weights."""
    keys = set(current) | set(target)
    return 0.5 * sum(abs(target.get(key, 0.0) - current.get(key, 0.0)) for key in keys)
