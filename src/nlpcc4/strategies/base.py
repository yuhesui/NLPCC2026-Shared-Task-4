"""Base contracts for custom strategies."""

from dataclasses import dataclass, field
from typing import Mapping, Protocol


@dataclass(frozen=True)
class StrategyContext:
    """Leakage-safe inputs available to a strategy on one decision date."""

    decision_date: str
    track: str
    fund_pool: tuple[str, ...]
    historical_prices: Mapping[str, object]
    news: tuple[Mapping[str, object], ...] = ()
    current_portfolio: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyResult:
    """Strategy output before execution-layer trade conversion."""

    target_weights: Mapping[str, float]
    diagnostics: Mapping[str, object] = field(default_factory=dict)


class Strategy(Protocol):
    """Protocol implemented by all custom strategies."""

    name: str

    def compute_target_weights(self, context: StrategyContext) -> StrategyResult:
        """Return target weights using only leakage-safe context."""
        ...


def validate_target_weights(weights: Mapping[str, float], tolerance: float = 1e-8) -> None:
    """Validate basic target-weight invariants without changing weights."""
    if not weights:
        raise ValueError("target_weights must not be empty")

    for fund_id, weight in weights.items():
        if not isinstance(fund_id, str) or not fund_id:
            raise ValueError("all target weight keys must be non-empty fund ids")
        if weight < -tolerance:
            raise ValueError(f"negative target weight for {fund_id}: {weight}")

    total_weight = sum(weights.values())
    if total_weight > 1.0 + tolerance:
        raise ValueError(f"target weights sum above 1.0: {total_weight}")
