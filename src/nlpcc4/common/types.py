"""Lightweight shared types for target-weight based strategies."""

from dataclasses import dataclass, field
from typing import Mapping


TargetWeights = Mapping[str, float]


@dataclass(frozen=True)
class DecisionContext:
    """Leakage-safe inputs for one strategy decision point."""

    decision_date: str
    track: str
    fund_pool: tuple[str, ...]
    historical_prices: Mapping[str, object]
    news: tuple[Mapping[str, object], ...] = ()
    current_portfolio: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyOutput:
    """Strategy output before execution-layer conversion."""

    target_weights: TargetWeights
    diagnostics: Mapping[str, object] = field(default_factory=dict)
