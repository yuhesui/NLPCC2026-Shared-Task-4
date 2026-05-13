"""Target-weight validation and normalization utilities."""

from typing import Mapping


def validate_target_weights(weights: Mapping[str, float], tolerance: float = 1e-8) -> None:
    """Validate basic long-only target weight invariants."""
    if not weights:
        raise ValueError("target weights must not be empty")
    for fund_id, weight in weights.items():
        if not fund_id:
            raise ValueError("fund id must not be empty")
        if weight < -tolerance:
            raise ValueError(f"negative target weight for {fund_id}: {weight}")
    total = sum(weights.values())
    if total > 1.0 + tolerance:
        raise ValueError(f"target weights sum above 1.0: {total}")
