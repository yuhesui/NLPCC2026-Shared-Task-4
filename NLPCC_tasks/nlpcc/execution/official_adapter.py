"""Adapters between official server payloads and internal runtime objects."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
import json
from typing import Any, Mapping

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.position_sizing import holding_value


@dataclass(frozen=True)
class NormalizedPortfolioState:
    """Internal portfolio state with explicit value-based holdings.

    ``holdings`` contains monetary market value per asset, not share quantity.
    Local share-like inputs are converted using the current open price. Official
    inputs with ``value`` or ``market_value`` are copied as value.
    """

    cash: float
    holdings: dict[str, dict[str, float | str]]
    total_value: float
    holding_unit: str = "market_value"
    source_fields: dict[str, str] = field(default_factory=dict)

    def as_agent_portfolio(self) -> dict[str, Any]:
        return {
            "cash": self.cash,
            "capital": self.cash,
            "holdings": self.holdings,
            "total_value": self.total_value,
            "holding_unit": self.holding_unit,
            "source_fields": self.source_fields,
        }


def current_open_by_fund(
    historical_prices: Mapping[str, list[dict[str, Any]]] | None,
    fund_pool: tuple[str, ...],
) -> dict[str, float]:
    prices: dict[str, float] = {}
    for fund_id in fund_pool:
        rows = (historical_prices or {}).get(fund_id, [])
        if not rows:
            continue
        value = rows[-1].get("open")
        if value not in (None, ""):
            prices[fund_id] = float(value)
    return prices


def normalize_track(track: str | None) -> TrackName:
    if track in {"macro", "track1", "track_1", "track_a", "a", "A", "Track A", "Track 1"}:
        return "macro"
    if track in {"sector", "track2", "track_2", "track_b", "b", "B", "Track B", "Track 2"}:
        return "sector"
    if track is None:
        return "macro"
    raise ValueError(f"Unsupported track: {track!r}")


def normalize_portfolio_state(
    official_portfolio: Mapping[str, Any] | None,
    *,
    current_open_by_fund: Mapping[str, float] | None = None,
    fund_pool: tuple[str, ...] | None = None,
) -> NormalizedPortfolioState:
    payload = dict(official_portfolio or {})
    cash = float(payload.get("cash", payload.get("capital", 0.0)) or 0.0)
    holdings_payload = dict(payload.get("holdings", {}) or {})
    open_prices = dict(current_open_by_fund or {})
    allowed = set(fund_pool or holdings_payload.keys())

    holdings: dict[str, dict[str, float | str]] = {}
    source_fields: dict[str, str] = {}
    for fund_id, raw_holding in holdings_payload.items():
        if fund_id not in allowed:
            continue
        price = float(open_prices.get(fund_id, 0.0) or 0.0)
        value = holding_value(raw_holding, price)
        if value <= 0:
            continue
        if isinstance(raw_holding, Mapping) and ("value" in raw_holding or "market_value" in raw_holding):
            source_fields[fund_id] = "official_value"
        elif isinstance(raw_holding, Mapping):
            source_fields[fund_id] = "share_like_dict"
        else:
            source_fields[fund_id] = "share_like_number"
        holdings[fund_id] = {
            "value": float(value),
            "price": price,
            "holding_unit": "market_value",
        }

    reported_total = payload.get("total_value")
    total_value = float(reported_total) if reported_total not in (None, "") else cash + sum(
        float(item["value"]) for item in holdings.values()
    )
    if total_value <= 0:
        total_value = cash
    return NormalizedPortfolioState(
        cash=cash,
        holdings=holdings,
        total_value=total_value,
        source_fields=source_fields,
    )


def build_agent_input(
    *,
    track: str | None,
    fund_pool: list[str] | tuple[str, ...] | None,
    historical_prices: Mapping[str, list[dict[str, Any]]] | None,
    news: list[dict[str, Any]] | None,
    current_portfolio: Mapping[str, Any] | None,
) -> dict[str, Any]:
    resolved_track = normalize_track(track)
    pool = tuple(fund_pool or get_fund_pool(resolved_track))
    open_prices = current_open_by_fund(historical_prices, pool)
    normalized_portfolio = normalize_portfolio_state(
        current_portfolio,
        current_open_by_fund=open_prices,
        fund_pool=pool,
    )
    return {
        "track": resolved_track,
        "fund_pool": pool,
        "historical_prices": dict(historical_prices or {}),
        "news": list(news or []),
        "current_portfolio": normalized_portfolio.as_agent_portfolio(),
        "current_open_by_fund": open_prices,
        "portfolio_adapter": asdict(normalized_portfolio),
    }


def write_decision_trace(path: Path, trace: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(trace)
    payload.setdefault("created_at_local", datetime.now().isoformat(timespec="seconds"))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
