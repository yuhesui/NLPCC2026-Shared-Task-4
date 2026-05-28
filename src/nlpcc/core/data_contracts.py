"""Canonical data objects shared by agents and local tools.

The contracts are deliberately small and dependency-free. They describe what a
decision-time agent may receive, not every column that exists in raw official
CSV files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Literal


TrackName = Literal["macro", "sector"]
TradeAction = Literal["buy", "sell"]


class PriceVisibility(str, Enum):
    """Visibility state for a price bar at decision time."""

    HISTORICAL_FULL = "historical_full"
    CURRENT_OPEN_ONLY = "current_open_only"


@dataclass(frozen=True)
class RawNewsItem:
    """A raw official news record after source normalization."""

    source: str
    title: str
    content: str | None
    ranking: int | None
    publish_time: datetime | None
    trade_date: date | None = None
    content_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PriceBar:
    """One asset's visible price data for one trading date."""

    fund_id: str
    date_int: int
    open: float | None
    close: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    change: float | None = None
    pct_change: float | None = None
    return_: float | None = None
    visibility: PriceVisibility = PriceVisibility.HISTORICAL_FULL

    @property
    def unsafe_current_fields(self) -> dict[str, float]:
        """Return fields that must not be populated on current-day bars."""

        values = {
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "change": self.change,
            "pct_change": self.pct_change,
            "return": self.return_,
        }
        return {key: value for key, value in values.items() if value is not None}


@dataclass(frozen=True)
class PricePanel:
    """Visible price bars keyed by fund id."""

    bars_by_fund: dict[str, tuple[PriceBar, ...]]

    def all_bars(self) -> tuple[PriceBar, ...]:
        bars: list[PriceBar] = []
        for fund_bars in self.bars_by_fund.values():
            bars.extend(fund_bars)
        return tuple(bars)


@dataclass(frozen=True)
class Holding:
    fund_id: str
    shares: float = 0.0
    market_value: float = 0.0


@dataclass(frozen=True)
class PortfolioState:
    cash: float
    holdings: dict[str, Holding] = field(default_factory=dict)
    total_value: float | None = None

    def resolved_total_value(self) -> float:
        if self.total_value is not None:
            return self.total_value
        return self.cash + sum(holding.market_value for holding in self.holdings.values())


@dataclass(frozen=True)
class TargetWeights:
    weights: dict[str, float]
    cash_weight: float = 0.0

    def gross_exposure(self) -> float:
        return sum(abs(weight) for weight in self.weights.values())


@dataclass(frozen=True)
class OfficialTrade:
    """Official-compatible trade abstraction.

    Buys use cash amount. Sells use a percentage of current holdings.
    """

    fund_id: str
    action: TradeAction
    amount: float | None = None
    percentage: float | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"fund_id": self.fund_id, "action": self.action}
        if self.action == "buy":
            payload["amount"] = self.amount
        else:
            payload["percentage"] = self.percentage
        return payload


@dataclass(frozen=True)
class DecisionTrace:
    decision_id: str
    decision_date: int
    reason_codes: tuple[str, ...] = ()
    fallback_used: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DailyDecisionInput:
    """Canonical input object for one decision timestamp."""

    decision_date: int
    track: TrackName
    fund_pool: tuple[str, ...]
    news: tuple[RawNewsItem, ...]
    prices: PricePanel
    portfolio: PortfolioState
    trace: DecisionTrace | None = None


def official_trade_from_payload(payload: dict[str, Any]) -> OfficialTrade:
    """Convert an official server-style trade dict into a contract object."""

    action = payload.get("action")
    if action not in {"buy", "sell"}:
        raise ValueError(f"Unsupported trade action: {action!r}")
    return OfficialTrade(
        fund_id=str(payload["fund_id"]),
        action=action,
        amount=payload.get("amount"),
        percentage=payload.get("percentage"),
    )
