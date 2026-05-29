"""Turnover-control utilities."""

from __future__ import annotations

from collections.abc import Mapping

from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.target_weights import project_long_only_capped_weights


def portfolio_turnover(current_weights: Mapping[str, float], target_weights: Mapping[str, float]) -> float:
    assets = set(current_weights) | set(target_weights)
    return 0.5 * sum(abs(float(target_weights.get(asset, 0.0)) - float(current_weights.get(asset, 0.0))) for asset in assets)


def apply_turnover_limit(
    target_weights: Mapping[str, float],
    current_weights: Mapping[str, float],
    constraints: PortfolioConstraints,
) -> dict[str, float]:
    """Blend target toward current holdings when turnover exceeds the cap."""

    assets = tuple(sorted(set(target_weights) | set(current_weights)))
    if not assets:
        return {}
    turnover = portfolio_turnover(current_weights, target_weights)
    if turnover <= constraints.max_turnover or turnover <= 0:
        target_total = min(constraints.invested_weight, sum(max(0.0, float(weight)) for weight in target_weights.values()))
        return project_long_only_capped_weights(
            target_weights,
            assets,
            max_weight=constraints.max_weight,
            total=target_total,
        )
    blend = max(0.0, min(1.0, constraints.max_turnover / turnover))
    limited = {
        asset: float(current_weights.get(asset, 0.0))
        + blend * (float(target_weights.get(asset, 0.0)) - float(current_weights.get(asset, 0.0)))
        for asset in assets
    }
    return project_long_only_capped_weights(
        limited,
        assets,
        max_weight=constraints.max_weight,
        total=min(constraints.invested_weight, sum(max(0.0, float(weight)) for weight in limited.values())),
    )
