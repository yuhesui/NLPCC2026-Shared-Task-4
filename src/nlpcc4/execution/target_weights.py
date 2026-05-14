"""Target-weight validation and normalization utilities."""

from __future__ import annotations

import math
from typing import Mapping, Sequence


def clean_target_weights(
    weights: Mapping[str, float],
    *,
    universe: Sequence[str] | None = None,
    drop_tolerance: float = 1e-12,
) -> dict[str, float]:
    """Return finite non-negative weights, optionally aligned to a universe."""
    keys = tuple(universe) if universe is not None else tuple(weights.keys())
    cleaned: dict[str, float] = {}
    for asset in keys:
        value = float(weights.get(asset, 0.0))
        if not math.isfinite(value):
            raise ValueError(f"non-finite target weight for {asset}: {value}")
        if value > drop_tolerance:
            cleaned[asset] = value
        else:
            cleaned[asset] = 0.0
    return cleaned


def validate_target_weights(weights: Mapping[str, float], tolerance: float = 1e-8) -> None:
    """Validate basic long-only target weight invariants."""
    if not weights:
        raise ValueError("target weights must not be empty")
    for fund_id, weight in weights.items():
        if not fund_id:
            raise ValueError("fund id must not be empty")
        if not math.isfinite(float(weight)):
            raise ValueError(f"non-finite target weight for {fund_id}: {weight}")
        if weight < -tolerance:
            raise ValueError(f"negative target weight for {fund_id}: {weight}")
    total = sum(float(value) for value in weights.values())
    if total > 1.0 + tolerance:
        raise ValueError(f"target weights sum above 1.0: {total}")


def normalize_target_weights(
    weights: Mapping[str, float],
    *,
    target_sum: float = 1.0,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Normalize positive weights to a requested sum."""
    if target_sum < 0 or target_sum > 1.0:
        raise ValueError("target_sum must be in [0, 1]")
    cleaned = clean_target_weights(weights, universe=universe)
    positive_total = sum(max(0.0, value) for value in cleaned.values())
    if positive_total <= 0:
        if not cleaned:
            raise ValueError("cannot normalize empty target weights")
        equal = target_sum / len(cleaned)
        return {asset: equal for asset in cleaned}
    return {asset: max(0.0, value) / positive_total * target_sum for asset, value in cleaned.items()}


def weights_sum(weights: Mapping[str, float]) -> float:
    """Return total target weight."""
    return sum(float(value) for value in weights.values())
