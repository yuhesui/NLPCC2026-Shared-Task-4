"""Portfolio allocation constraints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class PortfolioConstraints:
    max_weight: float = 0.35
    cash_reserve: float = 0.03
    max_turnover: float = 0.25
    rebalance_threshold: float = 0.01
    long_only: bool = True

    @classmethod
    def from_mapping(cls, values: dict | None) -> "PortfolioConstraints":
        if not values:
            return cls()
        return cls(**{key: value for key, value in values.items() if key in cls.__dataclass_fields__})

    @property
    def invested_weight(self) -> float:
        return max(0.0, min(1.0, 1.0 - self.cash_reserve))


def validate_weight_constraints(weights: Mapping[str, float], constraints: PortfolioConstraints) -> list[str]:
    issues: list[str] = []
    if constraints.long_only and any(weight < -1e-10 for weight in weights.values()):
        issues.append("negative_weight")
    if any(weight > constraints.max_weight + 1e-8 for weight in weights.values()):
        issues.append("concentration_limit")
    if sum(max(0.0, weight) for weight in weights.values()) > constraints.invested_weight + 1e-8:
        issues.append("cash_reserve")
    return issues
