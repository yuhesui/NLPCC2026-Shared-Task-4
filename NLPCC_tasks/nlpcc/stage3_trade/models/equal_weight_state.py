"""Equal-weight baseline weights."""

from __future__ import annotations

from typing import Iterable


def normalize_weights(raw_weights: dict[str, float], total: float = 1.0) -> dict[str, float]:
    positive = {fund_id: max(0.0, float(weight)) for fund_id, weight in raw_weights.items()}
    gross = sum(positive.values())
    if gross <= 0:
        return {}
    return {fund_id: (weight / gross) * total for fund_id, weight in positive.items() if weight > 0}


def equal_weight(fund_pool: Iterable[str], total: float = 1.0) -> dict[str, float]:
    funds = tuple(dict.fromkeys(fund_pool))
    if not funds:
        return {}
    weight = total / len(funds)
    return {fund_id: weight for fund_id in funds}


def cap_and_redistribute(weights: dict[str, float], max_weight: float, total: float = 1.0) -> dict[str, float]:
    """Apply a simple long-only cap and redistribute excess to uncapped assets."""

    if not weights:
        return {}
    max_weight = max(0.0, min(max_weight, total))
    capped = {fund_id: 0.0 for fund_id in weights}
    remaining = normalize_weights(weights, total)
    while remaining:
        overweight = {fund_id: weight for fund_id, weight in remaining.items() if weight > max_weight}
        if not overweight:
            for fund_id, weight in remaining.items():
                capped[fund_id] += weight
            break
        for fund_id in overweight:
            capped[fund_id] += max_weight
            remaining.pop(fund_id, None)
        budget = total - sum(capped.values())
        if budget <= 0 or not remaining:
            break
        remaining = normalize_weights(remaining, budget)
    return {fund_id: weight for fund_id, weight in capped.items() if weight > 0}
