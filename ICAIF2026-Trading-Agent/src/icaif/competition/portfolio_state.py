"""Portfolio state (cash + fractional shares) and drift.

The official portfolio API response schema is not documented in the starter
kit (only the endpoint ``/api/v1/me/portfolio``). :func:`parse_portfolio_payload`
therefore accepts a small set of explicit shapes and raises
:class:`PortfolioStateIncomplete` for anything else — the runtime then holds
(submits nothing) instead of guessing. Verify the shape during Validation
(docs/operations/LIVE_RUNBOOK.md, step "portfolio schema check").
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

from icaif.core.constants import INITIAL_NAV
from icaif.core.universe import SYMBOL_INDEX, SYMBOLS


class PortfolioStateIncomplete(ValueError):
    pass


@dataclass(frozen=True)
class PortfolioState:
    cash: float
    shares: tuple[float, ...]  # official symbol order, fractional allowed
    as_of: datetime | None = None
    reference_prices: tuple[float, ...] | None = None
    source: str = "local"
    raw_nav: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.shares) != len(SYMBOLS):
            raise PortfolioStateIncomplete("shares must cover all 30 symbols")
        if not math.isfinite(self.cash):
            raise PortfolioStateIncomplete("cash must be finite")
        if any((not math.isfinite(s)) or s < -1e-9 for s in self.shares):
            raise PortfolioStateIncomplete("shares must be finite and non-negative (long-only)")

    @classmethod
    def initial(cls, nav: float = INITIAL_NAV) -> PortfolioState:
        return cls(cash=nav, shares=(0.0,) * len(SYMBOLS), source="initial")

    def market_values(self, prices: np.ndarray) -> np.ndarray:
        return np.asarray(self.shares, dtype=float) * np.asarray(prices, dtype=float)

    def nav(self, prices: np.ndarray) -> float:
        return float(self.cash + self.market_values(prices).sum())

    def weights(self, prices: np.ndarray) -> np.ndarray:
        """Current (drifted) weights at ``prices``; zero vector if NAV <= 0."""

        nav = self.nav(prices)
        if nav <= 0:
            return np.zeros(len(SYMBOLS))
        return self.market_values(prices) / nav

    def weights_dict(self, prices: np.ndarray) -> dict[str, float]:
        return dict(zip(SYMBOLS, (float(x) for x in self.weights(prices)), strict=True))


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or value is None:
        raise PortfolioStateIncomplete(f"{label} missing or non-numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise PortfolioStateIncomplete(f"{label} is not numeric") from error
    if not math.isfinite(number):
        raise PortfolioStateIncomplete(f"{label} is not finite")
    return number


def parse_portfolio_payload(payload: Mapping[str, Any]) -> PortfolioState:
    """Parse an organizer portfolio response.

    Accepted shapes (any other raises):

    * ``{"cash": x, "positions": {"AAPL": {"shares"|"quantity": q, "price"?: p}, ...}}``
    * ``{"cash": x, "positions": [{"symbol": "AAPL", "shares"|"quantity": q, "price"?: p}, ...]}``
    * ``{"cash": x, "holdings": ...}`` (same as ``positions``)

    Optional top-level ``nav``/``total_value`` and ``as_of`` are retained for
    reconciliation. Symbols absent from positions are zero holdings; unknown
    symbols are an error.
    """

    if not isinstance(payload, Mapping):
        raise PortfolioStateIncomplete("portfolio payload must be an object")
    body = payload.get("portfolio", payload)
    if not isinstance(body, Mapping) or "cash" not in body:
        raise PortfolioStateIncomplete("portfolio payload lacks cash")
    cash = _number(body["cash"], "cash")
    positions = body.get("positions", body.get("holdings"))
    if positions is None:
        raise PortfolioStateIncomplete("portfolio payload lacks positions/holdings")
    rows: list[tuple[str, Mapping[str, Any]]] = []
    if isinstance(positions, Mapping):
        rows = [(str(k), v if isinstance(v, Mapping) else {"shares": v}) for k, v in positions.items()]
    elif isinstance(positions, list):
        for item in positions:
            if not isinstance(item, Mapping) or "symbol" not in item:
                raise PortfolioStateIncomplete("position rows need a symbol")
            rows.append((str(item["symbol"]), item))
    else:
        raise PortfolioStateIncomplete("positions must be an object or list")
    shares = [0.0] * len(SYMBOLS)
    prices: list[float | None] = [None] * len(SYMBOLS)
    for symbol, row in rows:
        if symbol not in SYMBOL_INDEX:
            raise PortfolioStateIncomplete(f"unknown symbol in portfolio: {symbol}")
        quantity = row.get("shares", row.get("quantity"))
        shares[SYMBOL_INDEX[symbol]] = _number(quantity, f"{symbol}.shares")
        if row.get("price") is not None:
            prices[SYMBOL_INDEX[symbol]] = _number(row["price"], f"{symbol}.price")
    nav_value = body.get("nav", body.get("total_value"))
    as_of = None
    if body.get("as_of"):
        from icaif.core.time import parse_timestamp

        as_of = parse_timestamp(str(body["as_of"]), "portfolio.as_of")
    reference = tuple(p if p is not None else math.nan for p in prices) if any(p is not None for p in prices) else None
    return PortfolioState(
        cash=cash,
        shares=tuple(shares),
        as_of=as_of,
        reference_prices=reference,
        source="official_api",
        raw_nav=_number(nav_value, "nav") if nav_value is not None else None,
    )
