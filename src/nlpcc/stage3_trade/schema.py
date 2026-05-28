"""Stage 3 market/risk-state schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Stage3Config:
    volatility_window: int = 20
    momentum_windows: tuple[int, ...] = (3, 5, 20)
    sector_trend_window: int = 20
    breadth_window: int = 20
    drawdown_window: int = 20
    shrinkage_alpha: float = 0.2
    max_weight: float = 0.35
    cash_reserve: float = 0.02
    rebalance_threshold: float = 0.01

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "Stage3Config":
        if not values:
            return cls()
        data = dict(values)
        if "momentum_windows" in data:
            data["momentum_windows"] = tuple(int(item) for item in data["momentum_windows"])
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})


@dataclass(frozen=True)
class AssetTradeState:
    fund_id: str
    current_open: float | None
    last_close: float | None
    prior_closes: tuple[float, ...]
    prior_returns: tuple[float, ...]
    volatility: float
    momentum: float
    drawdown: float
    breadth: float


@dataclass(frozen=True)
class Stage3State:
    decision_date: int
    fund_pool: tuple[str, ...]
    assets: dict[str, AssetTradeState]
    equal_weight: dict[str, float]
    inverse_volatility_weight: dict[str, float]
    momentum_weight: dict[str, float]
    sector_trend_weight: dict[str, float]
    covariance: dict[str, dict[str, float]]
    shrinkage_covariance: dict[str, dict[str, float]]
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def available_funds(self) -> tuple[str, ...]:
        return tuple(fund_id for fund_id in self.fund_pool if fund_id in self.assets)

    def current_open_by_fund(self) -> dict[str, float]:
        return {
            fund_id: asset.current_open
            for fund_id, asset in self.assets.items()
            if asset.current_open is not None and asset.current_open > 0
        }
