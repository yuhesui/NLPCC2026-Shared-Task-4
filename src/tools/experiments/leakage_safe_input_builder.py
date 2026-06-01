"""Leakage-safe daily input construction for official-semantics experiments."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from nlpcc.core.fund_universe import TrackName, get_fund_pool


NEWS_CUTOFF_HOUR = 15


@dataclass(frozen=True)
class LeakageSafeDayInput:
    date: str
    track: TrackName
    fund_pool: tuple[str, ...]
    historical_prices: dict[str, list[dict[str, Any]]]
    news: list[dict[str, Any]]
    current_portfolio: dict[str, Any]
    diagnostics: dict[str, Any]


@dataclass(frozen=True)
class MarketArrays:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    open_prices: np.ndarray
    pct_changes: np.ndarray


class LeakageSafeInputBuilder:
    """Builds the payload shape consumed by ``SystemRunner.run_day``.

    Current-day rows expose only ``open`` to strategy code. Close/high/low and
    return columns are set to ``None`` until the official-semantics replay step.
    """

    def __init__(
        self,
        *,
        data_root: Path,
        track: TrackName,
        lookback_days: int = 60,
        news_lookback_calendar_days: int = 1,
        top_news_rank: int = 20,
    ) -> None:
        self.data_root = Path(data_root)
        self.track = track
        self.lookback_days = max(1, int(lookback_days))
        self.news_lookback_calendar_days = max(1, int(news_lookback_calendar_days))
        self.top_news_rank = max(1, int(top_news_rank))
        self.assets = tuple(
            fund_id for fund_id in get_fund_pool(track) if (self.data_root / "price_data" / f"{fund_id}.csv").exists()
        )
        if not self.assets:
            raise RuntimeError(f"No price files for {track} under {self.data_root}")
        self._price_rows = {asset: self._load_price_rows(asset) for asset in self.assets}
        self._price_index = {asset: {row["date"]: index for index, row in enumerate(rows)} for asset, rows in self._price_rows.items()}
        common_dates: set[str] | None = None
        for rows in self._price_rows.values():
            dates = {row["date"] for row in rows}
            common_dates = dates if common_dates is None else common_dates & dates
        self._common_dates = tuple(sorted(common_dates or ()))
        self._news_cache: list[tuple[Any, datetime, int, dict[str, Any]]] | None = None

    def selected_dates(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        max_dates: int | None = None,
    ) -> tuple[str, ...]:
        start_int = _date_int(start_date) if start_date else None
        end_int = _date_int(end_date) if end_date else None
        dates = tuple(
            date
            for date in self._common_dates
            if (start_int is None or int(date) >= start_int) and (end_int is None or int(date) <= end_int)
        )
        if max_dates is not None:
            dates = dates[: max(1, int(max_dates))]
        if not dates:
            raise RuntimeError(f"No selected dates for {self.track} under {self.data_root}")
        return dates

    def market_arrays(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        max_dates: int | None = None,
    ) -> MarketArrays:
        dates = self.selected_dates(start_date=start_date, end_date=end_date, max_dates=max_dates)
        open_prices = np.empty((len(dates), len(self.assets)), dtype=float)
        pct_changes = np.empty_like(open_prices)
        for asset_index, asset in enumerate(self.assets):
            rows = self._price_rows[asset]
            index_by_date = self._price_index[asset]
            for date_index, day in enumerate(dates):
                row = rows[index_by_date[day]]
                open_prices[date_index, asset_index] = float(row["open"])
                pct_changes[date_index, asset_index] = float(row.get("pctchange", 0.0) or 0.0)
        return MarketArrays(dates=dates, assets=self.assets, open_prices=open_prices, pct_changes=pct_changes)

    def build_day(
        self,
        *,
        decision_date: str,
        current_portfolio: Mapping[str, Any],
        load_news: bool,
    ) -> LeakageSafeDayInput:
        historical_prices = {
            asset: self._safe_price_window(asset, decision_date)
            for asset in self.assets
            if decision_date in self._price_index[asset]
        }
        news = self.visible_news(decision_date) if load_news else []
        diagnostics = {
            "current_day_close_masked": all(rows and rows[-1].get("close") is None for rows in historical_prices.values()),
            "current_day_open_available": all(rows and rows[-1].get("open") is not None for rows in historical_prices.values()),
            "news_cutoff_hour": NEWS_CUTOFF_HOUR,
            "news_count": len(news),
            "lookback_days": self.lookback_days,
            "forbidden_current_fields": ("close", "high", "low", "change", "pct_change"),
        }
        return LeakageSafeDayInput(
            date=decision_date,
            track=self.track,
            fund_pool=self.assets,
            historical_prices=historical_prices,
            news=news,
            current_portfolio=dict(current_portfolio),
            diagnostics=diagnostics,
        )

    def visible_news(self, decision_date: str) -> list[dict[str, Any]]:
        current_day = datetime.strptime(decision_date, "%Y%m%d").date()
        if self._news_cache is None:
            self._news_cache = self._load_all_news_rows()
        earliest_news_day = current_day - timedelta(days=self.news_lookback_calendar_days - 1)
        records: list[dict[str, Any]] = []
        for news_day, published, ranking, row in self._news_cache:
            if news_day < earliest_news_day or news_day > current_day:
                continue
            if news_day == current_day and published.hour >= NEWS_CUTOFF_HOUR:
                continue
            if ranking > self.top_news_rank:
                continue
            records.append(row)
        records.sort(key=lambda item: int(item.get("RANKING", item.get("ranking", "999")) or 999))
        return records

    def _safe_price_window(self, asset: str, decision_date: str) -> list[dict[str, Any]]:
        rows = self._price_rows[asset]
        current_index = self._price_index[asset][decision_date]
        start = max(0, current_index - self.lookback_days + 1)
        output: list[dict[str, Any]] = []
        for index in range(start, current_index):
            output.append(_full_price_row(rows[index]))
        current = rows[current_index]
        output.append(
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
        return output

    def _load_price_rows(self, fund_id: str) -> list[dict[str, str]]:
        path = self.data_root / "price_data" / f"{fund_id}.csv"
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise RuntimeError(f"Empty price file: {path}")
        return rows

    def _load_all_news_rows(self) -> list[tuple[Any, datetime, int, dict[str, Any]]]:
        news_dir = self.data_root / "news_data"
        rows: list[tuple[Any, datetime, int, dict[str, Any]]] = []
        if not news_dir.exists():
            return rows
        for path in sorted(news_dir.glob("*_daily_dedup.csv")):
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    try:
                        news_day = datetime.strptime(str(row.get("THEDATE", ""))[:10], "%Y-%m-%d").date()
                        published = datetime.strptime(str(row.get("PUBLISH_TIME", ""))[:19], "%Y-%m-%d %H:%M:%S")
                        ranking = int(row.get("RANKING", "999") or 999)
                    except ValueError:
                        continue
                    rows.append((news_day, published, ranking, row))
        return rows


def portfolio_payload(cash: float, holdings: Mapping[str, float], assets: tuple[str, ...], open_row: np.ndarray) -> dict[str, Any]:
    return {
        "cash": float(cash),
        "capital": float(cash),
        "holdings": {
            asset: {"value": float(holdings.get(asset, 0.0)), "price": float(open_row[index])}
            for index, asset in enumerate(assets)
            if holdings.get(asset, 0.0) > 1e-9
        },
        "total_value": float(cash) + sum(float(value) for value in holdings.values() if value > 0),
    }


def open_payload(assets: tuple[str, ...], open_row: np.ndarray) -> dict[str, float]:
    return {asset: float(open_row[index]) for index, asset in enumerate(assets)}


def _full_price_row(row: Mapping[str, str]) -> dict[str, Any]:
    return {
        "date_int": int(row["date"]),
        "open": float(row["open"]),
        "close": float(row["close"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "change": float(row.get("change", 0.0) or 0.0),
        "pct_change": float(row.get("pctchange", 0.0) or 0.0),
    }


def _date_int(value: str) -> int:
    digits = "".join(char for char in str(value) if char.isdigit())
    return int(digits[:8])
