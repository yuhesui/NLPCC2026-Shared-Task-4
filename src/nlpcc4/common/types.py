"""Shared typed contracts for target-weight-first strategy code."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping, Sequence


TargetWeights = Mapping[str, float]


@dataclass(frozen=True)
class PriceBar:
    """Official-compatible daily price record visible to a strategy."""

    date: str
    date_int: int
    open: float | None = None
    close: float | None = None
    high: float | None = None
    low: float | None = None
    change: float | None = None
    pct_change: float | None = None


@dataclass(frozen=True)
class NewsItem:
    """Normalized news item used by custom strategies."""

    source: str
    title: str
    content: str = ""
    ranking: int | None = None
    publish_time: str | None = None
    date: str | None = None


@dataclass(frozen=True)
class PortfolioState:
    """Portfolio state expressed in official monetary-value semantics."""

    cash: float
    holdings: Mapping[str, float] = field(default_factory=dict)
    total_value: float | None = None

    def value(self) -> float:
        if self.total_value is not None:
            return float(self.total_value)
        return float(self.cash + sum(self.holdings.values()))

    def weights(self) -> dict[str, float]:
        total = self.value()
        if total <= 0:
            return {asset: 0.0 for asset in self.holdings}
        return {asset: float(value) / total for asset, value in self.holdings.items()}


@dataclass(frozen=True)
class DecisionContext:
    """Leakage-safe inputs for one strategy decision point."""

    decision_date: str
    track: str
    fund_pool: tuple[str, ...]
    historical_prices: Mapping[str, Sequence[Mapping[str, Any]]]
    news: tuple[Mapping[str, Any], ...] = ()
    current_portfolio: Mapping[str, Any] = field(default_factory=dict)
    previous_weights: Mapping[str, float] = field(default_factory=dict)
    config: Mapping[str, Any] = field(default_factory=dict)
    run_id: str = ""
    llm_mode: str = "off"
    dry_run: bool = False


@dataclass(frozen=True)
class StrategyOutput:
    """Strategy output before execution-layer conversion."""

    target_weights: TargetWeights
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


StrategyDecision = StrategyOutput


@dataclass(frozen=True)
class TradeInstruction:
    """Official trade API compatible instruction."""

    fund_id: str
    action: str
    amount: float | None = None
    percentage: float | None = None

    def to_payload(self) -> dict[str, float | str]:
        payload: MutableMapping[str, float | str] = {
            "fund_id": self.fund_id,
            "action": self.action,
        }
        if self.action == "buy" and self.amount is not None:
            payload["amount"] = float(self.amount)
        if self.action == "sell" and self.percentage is not None:
            payload["percentage"] = float(self.percentage)
        return dict(payload)


@dataclass(frozen=True)
class RunMetadata:
    """Reproducibility metadata for local runs."""

    run_id: str
    track: str
    strategy: str
    config_path: str
    start_date: str
    end_date: str
    llm_mode: str
