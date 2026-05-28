"""Shrink sample covariance toward a diagonal target."""

from __future__ import annotations


def shrink_covariance(
    covariance: dict[str, dict[str, float]],
    *,
    alpha: float = 0.2,
) -> dict[str, dict[str, float]]:
    if not covariance:
        return {}
    alpha = max(0.0, min(1.0, alpha))
    funds = sorted(covariance)
    variances = [max(0.0, covariance[fund_id].get(fund_id, 0.0)) for fund_id in funds]
    average_variance = sum(variances) / len(variances) if variances else 0.0
    shrunk: dict[str, dict[str, float]] = {}
    for left in funds:
        shrunk[left] = {}
        for right in funds:
            sample = covariance[left].get(right, 0.0)
            target = average_variance if left == right else 0.0
            shrunk[left][right] = ((1.0 - alpha) * sample) + (alpha * target)
    return shrunk
