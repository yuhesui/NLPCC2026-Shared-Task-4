"""Deterministic tiny-buy smoke agent.

The agent is intentionally simple: it chooses the first asset in the selected
track and buys a small cash amount when there is available cash. It may read the
current-day open from the safe historical price payload, but it never reads
current-day close/high/low/change/return fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool


FORBIDDEN_CURRENT_DAY_FIELDS = frozenset(
    {"close", "high", "low", "change", "pctchange", "pct_change", "return"}
)


@dataclass(frozen=True)
class SmokeOneUnitAgent:
    """A deterministic first-asset tiny-buy agent for plumbing checks."""

    notional: float = 100.0

    def make_decision(
        self,
        *,
        track: TrackName = "macro",
        fund_pool: list[str] | tuple[str, ...] | None = None,
        historical_prices: dict[str, list[dict[str, Any]]] | None = None,
        news: list[dict[str, Any]] | None = None,
        current_portfolio: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        pool = tuple(fund_pool or get_fund_pool(track))
        if not pool:
            return self._hold("empty_fund_pool", news, historical_prices)

        selected = pool[0]
        historical_prices = historical_prices or {}
        news = news or []
        current_portfolio = current_portfolio or {}
        cash = float(current_portfolio.get("cash", current_portfolio.get("capital", 0.0)) or 0.0)
        holdings = current_portfolio.get("holdings", {}) or {}

        current_open = self._safe_current_open(historical_prices.get(selected, []))
        if holdings.get(selected):
            return self._hold("already_holding_first_asset", news, historical_prices, selected, current_open)

        amount = min(self.notional, cash) if cash > 0 else self.notional
        if amount <= 0:
            return self._hold("no_available_cash", news, historical_prices, selected, current_open)

        return {
            "trades": [{"fund_id": selected, "action": "buy", "amount": round(amount, 2)}],
            "reasoning": "prompt01 deterministic smoke: buy tiny fixed cash amount in first track asset.",
            "metadata": {
                "track": track,
                "selected_fund": selected,
                "news_items_read": len(news),
                "price_series_read": len(historical_prices.get(selected, [])),
                "current_open_read": current_open,
                "forbidden_current_fields_used": [],
            },
        }

    @staticmethod
    def _safe_current_open(price_records: list[dict[str, Any]]) -> float | None:
        if not price_records:
            return None
        current_record = price_records[-1]
        value = current_record.get("open")
        return float(value) if value not in (None, "") else None

    @staticmethod
    def _hold(
        reason: str,
        news: list[dict[str, Any]] | None,
        historical_prices: dict[str, list[dict[str, Any]]] | None,
        selected_fund: str | None = None,
        current_open: float | None = None,
    ) -> dict[str, Any]:
        return {
            "trades": [],
            "reasoning": f"prompt01 deterministic smoke hold: {reason}.",
            "metadata": {
                "selected_fund": selected_fund,
                "news_items_read": len(news or []),
                "price_assets_read": len(historical_prices or {}),
                "current_open_read": current_open,
                "forbidden_current_fields_used": [],
            },
        }


def make_smoke_decision(**kwargs: Any) -> dict[str, Any]:
    """Convenience wrapper used by runner scripts."""

    return SmokeOneUnitAgent().make_decision(**kwargs)
