"""Deterministic local backtester for smoke and baseline research runs.

It masks the current decision day's close/high/low/change/return fields before
calling the agent, then uses the same day's close only for post-decision
execution.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.stage4_agent.models.smoke_one_unit_agent import SmokeOneUnitAgent
from tools.backtesting.metrics import compute_backtest_metrics


COMMISSION_RATE = 0.0001
NEWS_CUTOFF_HOUR = 15


@dataclass
class LocalSmokeBacktester:
    data_root: Path
    track: TrackName = "macro"
    initial_capital: float = 100000.0
    lookback_days: int = 2
    agent: Any = field(default_factory=SmokeOneUnitAgent)
    load_news: bool = True

    def run(self, output_path: Path | None = None) -> dict[str, Any]:
        official_pool = get_fund_pool(self.track)
        fund_pool = tuple(fund_id for fund_id in official_pool if (self.data_root / "price_data" / f"{fund_id}.csv").exists())
        if not fund_pool:
            raise RuntimeError(f"No price rows available for track {self.track} under {self.data_root}")
        selected = fund_pool[0]
        price_rows_by_fund = {fund_id: self._load_price_rows(fund_id) for fund_id in fund_pool}
        date_count = min(len(rows) for rows in price_rows_by_fund.values())
        if date_count <= 0:
            raise RuntimeError(f"Empty price rows for track {self.track} under {self.data_root}")

        cash = self.initial_capital
        holdings: dict[str, float] = {}
        previous_weights: dict[str, float] = {}
        weight_history: list[dict[str, float]] = []
        decisions: list[dict[str, Any]] = []
        transactions: list[dict[str, Any]] = []
        portfolio_history: list[dict[str, Any]] = []

        for index in range(date_count):
            row = price_rows_by_fund[selected][index]
            current_date = row["date"]
            safe_prices = {
                fund_id: self._safe_price_window(rows, index)
                for fund_id, rows in price_rows_by_fund.items()
            }
            news = self._load_news(current_date) if self.load_news else []
            portfolio = {"cash": cash, "holdings": holdings.copy()}
            decision = self.agent.make_decision(
                track=self.track,
                fund_pool=fund_pool,
                historical_prices=safe_prices,
                news=news,
                current_portfolio=portfolio,
            )
            decisions.append({"date": current_date, "decision": decision})

            close_by_fund = {fund_id: float(rows[index]["close"]) for fund_id, rows in price_rows_by_fund.items()}
            cash_at_decision = cash
            buy_spent = 0.0
            for trade in [item for item in decision.get("trades", []) if item.get("action") == "buy"]:
                fund_id = str(trade.get("fund_id"))
                if fund_id not in close_by_fund:
                    continue
                requested = float(trade.get("amount", 0.0) or 0.0)
                amount = min(requested, max(0.0, cash_at_decision - buy_spent), cash)
                if amount <= 0:
                    continue
                close_price = close_by_fund[fund_id]
                commission = amount * COMMISSION_RATE
                shares = (amount - commission) / close_price
                cash -= amount
                buy_spent += amount
                holdings[fund_id] = holdings.get(fund_id, 0.0) + shares
                transactions.append(
                    {
                        "date": current_date,
                        "fund_id": fund_id,
                        "action": "buy",
                        "amount": round(amount, 6),
                        "execution_price": close_price,
                        "commission": round(commission, 6),
                        "shares": round(shares, 10),
                    }
                )

            for trade in [item for item in decision.get("trades", []) if item.get("action") == "sell"]:
                fund_id = str(trade.get("fund_id"))
                if fund_id not in close_by_fund:
                    continue
                percentage = max(0.0, min(1.0, float(trade.get("percentage", 0.0) or 0.0)))
                shares_to_sell = holdings.get(fund_id, 0.0) * percentage
                if shares_to_sell <= 0:
                    continue
                close_price = close_by_fund[fund_id]
                gross = shares_to_sell * close_price
                commission = gross * COMMISSION_RATE
                cash += gross - commission
                holdings[fund_id] = max(0.0, holdings.get(fund_id, 0.0) - shares_to_sell)
                transactions.append(
                    {
                        "date": current_date,
                        "fund_id": fund_id,
                        "action": "sell",
                        "percentage": round(percentage, 6),
                        "amount_sold": round(gross, 6),
                        "execution_price": close_price,
                        "commission": round(commission, 6),
                        "shares": round(shares_to_sell, 10),
                    }
                )

            holdings_value_by_fund = {
                fund_id: shares * close_by_fund.get(fund_id, 0.0)
                for fund_id, shares in holdings.items()
                if shares > 0 and fund_id in close_by_fund
            }
            holdings_value = sum(holdings_value_by_fund.values())
            total_value = cash + holdings_value
            current_weights = {
                fund_id: value / total_value
                for fund_id, value in holdings_value_by_fund.items()
                if total_value > 0 and value > 0
            }
            weight_history.append(current_weights)
            previous_weights = current_weights
            portfolio_history.append(
                {
                    "date": current_date,
                    "cash": round(cash, 6),
                    "holdings_value": round(holdings_value, 6),
                    "total_value": round(total_value, 6),
                    "weights": {fund_id: round(weight, 8) for fund_id, weight in previous_weights.items()},
                }
            )

        metrics = compute_backtest_metrics(
            [item["total_value"] for item in portfolio_history],
            weight_history=weight_history,
        ).as_dict()
        result = {
            "status": "ok",
            "track": self.track,
            "selected_fund": selected,
            "fund_pool": list(fund_pool),
            "initial_capital": self.initial_capital,
            "final_value": portfolio_history[-1]["total_value"],
            "metrics": metrics,
            "transactions": transactions,
            "decisions": decisions,
            "portfolio_history": portfolio_history,
            "leakage_note": "Current-day close/high/low/change/pct_change are masked before agent decision; close is used only for post-decision execution.",
        }
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result

    def _load_price_rows(self, fund_id: str) -> list[dict[str, str]]:
        path = self.data_root / "price_data" / f"{fund_id}.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _safe_price_window(self, rows: list[dict[str, str]], current_index: int) -> list[dict[str, Any]]:
        start = max(0, current_index - self.lookback_days + 1)
        records: list[dict[str, Any]] = []
        for idx in range(start, current_index):
            row = rows[idx]
            records.append(
                {
                    "date_int": int(row["date"]),
                    "open": float(row["open"]),
                    "close": float(row["close"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "change": float(row.get("change", 0.0) or 0.0),
                    "pct_change": float(row.get("pctchange", 0.0) or 0.0),
                }
            )
        current = rows[current_index]
        records.append(
            {
                "date_int": int(current["date"]),
                "open": float(current["open"]),
                "close": None,
                "high": None,
                "low": None,
                "change": None,
                "pct_change": None,
            }
        )
        return records

    def _load_news(self, current_date: str) -> list[dict[str, Any]]:
        news_dir = self.data_root / "news_data"
        current_day = datetime.strptime(current_date, "%Y%m%d").date()
        records: list[dict[str, Any]] = []
        for path in sorted(news_dir.glob("*_daily_dedup.csv")):
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    try:
                        news_day = datetime.strptime(row["THEDATE"], "%Y-%m-%d").date()
                        published = datetime.strptime(row["PUBLISH_TIME"], "%Y-%m-%d %H:%M:%S")
                        ranking = int(row.get("RANKING", "999"))
                    except (KeyError, ValueError):
                        continue
                    if news_day > current_day:
                        continue
                    if news_day == current_day and published.hour >= NEWS_CUTOFF_HOUR:
                        continue
                    if ranking > 20:
                        continue
                    records.append(row)
        records.sort(key=lambda item: int(item.get("RANKING", "999")))
        return records


LocalBacktester = LocalSmokeBacktester


def run_local_backtest(
    *,
    data_root: Path,
    track: TrackName,
    agent: Any,
    output_path: Path | None = None,
    lookback_days: int = 60,
    load_news: bool = False,
    initial_capital: float = 100000.0,
) -> dict[str, Any]:
    return LocalSmokeBacktester(
        data_root=data_root,
        track=track,
        agent=agent,
        lookback_days=lookback_days,
        load_news=load_news,
        initial_capital=initial_capital,
    ).run(output_path)
