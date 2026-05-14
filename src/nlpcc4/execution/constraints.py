"""Portfolio constraint projection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from nlpcc4.execution.target_weights import clean_target_weights, validate_target_weights


@dataclass(frozen=True)
class ConstraintConfig:
    """Common long-only portfolio constraints."""

    max_weight: float = 1.0
    cash_buffer: float = 0.0
    target_weight_sum_max: float = 1.0

    @property
    def investable_weight(self) -> float:
        return max(0.0, min(self.target_weight_sum_max, 1.0 - self.cash_buffer))


def _redistribute_with_cap(weights: dict[str, float], target_sum: float, cap: float) -> dict[str, float]:
    if not weights:
        return {}
    cap = max(0.0, min(cap, target_sum if target_sum > 0 else cap))
    remaining_assets = set(weights)
    result = {asset: 0.0 for asset in weights}
    remaining_sum = target_sum
    raw = {asset: max(0.0, value) for asset, value in weights.items()}
    while remaining_assets and remaining_sum > 1e-12:
        raw_total = sum(raw[asset] for asset in remaining_assets)
        if raw_total <= 0:
            equal = min(cap, remaining_sum / len(remaining_assets))
            for asset in list(remaining_assets):
                result[asset] += equal
                remaining_sum -= equal
                remaining_assets.remove(asset)
            break
        capped_this_round: list[str] = []
        for asset in list(remaining_assets):
            proposal = raw[asset] / raw_total * remaining_sum
            if proposal >= cap - 1e-12:
                result[asset] = cap
                capped_this_round.append(asset)
        if not capped_this_round:
            for asset in remaining_assets:
                result[asset] = raw[asset] / raw_total * remaining_sum
            remaining_sum = 0.0
            break
        for asset in capped_this_round:
            remaining_assets.remove(asset)
        remaining_sum = target_sum - sum(result.values())
    return {asset: max(0.0, min(cap, value)) for asset, value in result.items()}


def project_long_only(
    weights: Mapping[str, float],
    *,
    universe: Sequence[str] | None = None,
    max_weight: float | None = None,
    cash_buffer: float = 0.0,
    target_weight_sum_max: float = 1.0,
) -> dict[str, float]:
    """Project raw weights onto long-only, max-weight, cash-buffer constraints."""
    cleaned = clean_target_weights(weights, universe=universe)
    if not cleaned:
        raise ValueError("weights must not be empty")
    cap = 1.0 if max_weight is None else float(max_weight)
    if cap <= 0:
        raise ValueError("max_weight must be positive")
    target_sum = max(0.0, min(float(target_weight_sum_max), 1.0 - float(cash_buffer)))
    raw_total = sum(max(0.0, value) for value in cleaned.values())
    if raw_total <= 0:
        projected = {asset: target_sum / len(cleaned) for asset in cleaned}
    else:
        base = {asset: max(0.0, value) / raw_total * target_sum for asset, value in cleaned.items()}
        projected = _redistribute_with_cap(base, target_sum, cap)
    total = sum(projected.values())
    if total > target_sum + 1e-10:
        scale = target_sum / total
        projected = {asset: value * scale for asset, value in projected.items()}
    validate_target_weights(projected, tolerance=1e-7)
    return projected


def blend_weights(
    left: Mapping[str, float],
    right: Mapping[str, float],
    alpha: float,
    *,
    universe: Sequence[str] | None = None,
) -> dict[str, float]:
    """Blend two weight maps with alpha assigned to right."""
    alpha = max(0.0, min(1.0, alpha))
    keys = tuple(universe) if universe is not None else tuple(sorted(set(left) | set(right)))
    return {asset: (1.0 - alpha) * left.get(asset, 0.0) + alpha * right.get(asset, 0.0) for asset in keys}
