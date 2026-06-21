"""Small dependency-free covariance utilities."""

from __future__ import annotations


def sample_covariance(returns_by_fund: dict[str, list[float] | tuple[float, ...]]) -> dict[str, dict[str, float]]:
    funds = sorted(returns_by_fund)
    if not funds:
        return {}
    min_length = min((len(returns_by_fund[fund_id]) for fund_id in funds), default=0)
    if min_length < 2:
        return {left: {right: 0.0 for right in funds} for left in funds}

    aligned = {fund_id: tuple(returns_by_fund[fund_id][-min_length:]) for fund_id in funds}
    means = {fund_id: sum(values) / min_length for fund_id, values in aligned.items()}
    covariance: dict[str, dict[str, float]] = {}
    for left in funds:
        covariance[left] = {}
        for right in funds:
            value = sum(
                (aligned[left][idx] - means[left]) * (aligned[right][idx] - means[right])
                for idx in range(min_length)
            ) / (min_length - 1)
            covariance[left][right] = value
    return covariance
