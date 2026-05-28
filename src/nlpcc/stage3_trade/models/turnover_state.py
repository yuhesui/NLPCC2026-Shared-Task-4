"""Turnover-control helpers."""

from __future__ import annotations


def one_way_turnover(previous_weights: dict[str, float], target_weights: dict[str, float]) -> float:
    assets = set(previous_weights) | set(target_weights)
    return 0.5 * sum(abs(target_weights.get(asset, 0.0) - previous_weights.get(asset, 0.0)) for asset in assets)


def apply_rebalance_threshold(
    previous_weights: dict[str, float],
    target_weights: dict[str, float],
    *,
    threshold: float,
) -> dict[str, float]:
    if not previous_weights:
        return target_weights
    if one_way_turnover(previous_weights, target_weights) < threshold:
        return dict(previous_weights)
    return dict(target_weights)
