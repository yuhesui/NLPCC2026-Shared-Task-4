"""Adapters around the official leakage-safe DataLoader.

The wrapper prefers the starter-kit DataLoader when public CSVs are present.
This checkout may not include the ignored dataset files, so a deterministic
official-compatible synthetic loader is provided for offline tests and dry runs.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence

from nlpcc4.common.paths import official_starter_root


def _date_to_int(value: date) -> int:
    return int(value.strftime("%Y%m%d"))


def _int_to_date(value: int) -> date:
    return datetime.strptime(str(value), "%Y%m%d").date()


def _format_date(value: int) -> str:
    return datetime.strptime(str(value), "%Y%m%d").strftime("%Y-%m-%d")


def _asset_offset(asset: str) -> int:
    return sum(ord(ch) for ch in asset) % 97


def _business_dates(start: date, end: date) -> list[int]:
    current = start
    dates: list[int] = []
    while current <= end:
        if current.weekday() < 5:
            dates.append(_date_to_int(current))
        current += timedelta(days=1)
    return dates


class SyntheticOfficialCompatibleLoader:
    """Small deterministic data source matching the official DataLoader methods."""

    def __init__(self) -> None:
        self.trading_dates = _business_dates(date(2024, 1, 1), date(2026, 6, 30))

    def get_trading_dates(self, start_date: int, end_date: int) -> list[int]:
        return [day for day in self.trading_dates if start_date <= day <= end_date]

    def get_previous_trading_date(self, current_date: int, k: int = 1) -> int:
        dates = self.trading_dates
        idx = 0
        for i, day in enumerate(dates):
            if day >= current_date:
                idx = i
                break
        return dates[max(0, idx - k)]

    def _close(self, asset: str, day_int: int) -> float:
        day = _int_to_date(day_int)
        t = (day - date(2024, 1, 1)).days
        offset = _asset_offset(asset)
        base = 80.0 + offset
        trend = 1.0 + 0.00018 * t
        seasonal = 1.0 + 0.045 * math.sin((t + offset) / 23.0) + 0.018 * math.cos((t + offset) / 7.0)
        return max(1.0, base * trend * seasonal)

    def get_price_data(self, fund_ids: Sequence[str], date: int) -> dict[str, dict[str, float]]:
        result: dict[str, dict[str, float]] = {}
        previous = self.get_previous_trading_date(date, k=1)
        for fund_id in fund_ids:
            close = self._close(fund_id, date)
            prev_close = self._close(fund_id, previous)
            pct_change = (close / prev_close - 1.0) * 100.0 if prev_close else 0.0
            offset = _asset_offset(fund_id)
            open_price = prev_close * (1.0 + 0.15 * pct_change / 100.0)
            high = max(open_price, close) * (1.0 + 0.002 + (offset % 5) * 0.0003)
            low = min(open_price, close) * (1.0 - 0.002 - (offset % 3) * 0.0003)
            result[fund_id] = {
                "open": open_price,
                "close": close,
                "high": high,
                "low": low,
                "change": close - prev_close,
                "pct_change": pct_change,
                "volume": 1_000_000 + offset * 1000,
            }
        return result

    def get_historical_prices(
        self, fund_ids: Sequence[str], current_date: int, lookback_days: int
    ) -> dict[str, list[dict[str, Any]]]:
        dates = self.trading_dates
        try:
            current_idx = dates.index(current_date)
        except ValueError:
            current_idx = max(0, len([day for day in dates if day < current_date]) - 1)
        hist_end = current_idx - 1
        hist_start = max(0, hist_end - max(lookback_days - 2, 0))
        historical_dates = dates[hist_start : hist_end + 1] if hist_end >= 0 else []
        result: dict[str, list[dict[str, Any]]] = {fund: [] for fund in fund_ids}
        for day_int in historical_dates:
            price_data = self.get_price_data(fund_ids, day_int)
            for fund_id in fund_ids:
                row = price_data[fund_id]
                result[fund_id].append(
                    {
                        "date": _format_date(day_int),
                        "date_int": day_int,
                        "open": row["open"],
                        "close": row["close"],
                        "high": row["high"],
                        "low": row["low"],
                        "change": row["change"],
                        "pct_change": row["pct_change"],
                    }
                )
        current = dates[current_idx]
        current_prices = self.get_price_data(fund_ids, current)
        for fund_id in fund_ids:
            result[fund_id].append(
                {
                    "date": _format_date(current),
                    "date_int": current,
                    "open": current_prices[fund_id]["open"],
                    "close": None,
                    "high": None,
                    "low": None,
                    "change": None,
                    "pct_change": None,
                }
            )
        return result

    def get_historical_prices_for_funds(
        self, fund_ids: Sequence[str], start_date: int, end_date: int
    ) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {fund: [] for fund in fund_ids}
        for day_int in self.get_trading_dates(start_date, end_date):
            price_data = self.get_price_data(fund_ids, day_int)
            for fund_id in fund_ids:
                row = price_data[fund_id]
                result[fund_id].append(
                    {
                        "date": _format_date(day_int),
                        "date_int": day_int,
                        "open": row["open"],
                        "close": row["close"],
                        "high": row["high"],
                        "low": row["low"],
                        "change": row["change"],
                        "pct_change": row["pct_change"],
                    }
                )
        return result

    def get_benchmark_data(self, start_date: int, end_date: int) -> list[dict[str, Any]]:
        return [
            {"date": _format_date(day_int), "close": self._close("000300.SH", day_int)}
            for day_int in self.get_trading_dates(start_date, end_date)
        ]

    def get_news(
        self,
        sources: Sequence[str],
        current_date: int,
        top_rank: int = 10,
        pre_k_days: int = 1,
    ) -> list[dict[str, Any]]:
        previous = self.get_previous_trading_date(current_date, k=max(pre_k_days, 1))
        current_dt = _format_date(current_date)
        prev_dt = _format_date(previous)
        themes = [
            ("policy easing supports market liquidity", "policy liquidity easing"),
            ("commodity prices and energy supply remain in focus", "commodity energy inflation"),
            ("technology and semiconductor policy receives attention", "technology semiconductor policy"),
            ("defensive demand for bonds and gold rises", "risk defensive gold bond"),
        ]
        records: list[dict[str, Any]] = []
        for source_index, source in enumerate(sources):
            for rank, (title, content) in enumerate(themes[:top_rank], start=1):
                records.append(
                    {
                        "APP_TYPE": source,
                        "LIST_TYPE": "synthetic",
                        "THEDATE": prev_dt if rank % 2 == 0 else current_dt,
                        "TITLE": f"{title} ({source})",
                        "RANKING": rank + source_index,
                        "CONTENT_ID": f"{source}_{current_date}_{rank}",
                        "PUBLISH_TIME": f"{current_dt} 10:00:00",
                        "CONTENT": content,
                    }
                )
        records.sort(key=lambda item: item.get("RANKING", 999))
        return records[: max(top_rank, 0) * max(len(sources), 1)]


def _official_dataset_available(starter_root: Path) -> bool:
    price_dir = starter_root / "dataset" / "price_data" / "export_data"
    news_dir = starter_root / "dataset" / "news_data" / "export_data"
    return any(price_dir.glob("*.csv")) and any(news_dir.glob("*.csv"))


def load_official_data_loader() -> object:
    """Return the official DataLoader, or a deterministic compatible fallback."""
    starter_root = official_starter_root()
    if _official_dataset_available(starter_root):
        sys.path.insert(0, str(starter_root))
        from config import DATA_DIRS
        from server_platform.app.core.data_loader import DataLoader

        return DataLoader(str(DATA_DIRS["PRICE_DATA"]), str(DATA_DIRS["NEWS_DATA"]))
    return SyntheticOfficialCompatibleLoader()


@dataclass(frozen=True)
class OfficialDataPortal:
    """Convenience wrapper for strategy runner inputs."""

    loader: object
    same_day_news_policy: str = "previous_day_only"

    def trading_dates(self, start_date: str, end_date: str) -> list[int]:
        return self.loader.get_trading_dates(int(start_date.replace("-", "")), int(end_date.replace("-", "")))

    def historical_prices(
        self, fund_pool: Sequence[str], current_date: int, lookback_days: int
    ) -> dict[str, list[dict[str, Any]]]:
        return self.loader.get_historical_prices(list(fund_pool), current_date, lookback_days)

    def full_prices(
        self, fund_pool: Sequence[str], start_date: str, end_date: str
    ) -> dict[str, list[dict[str, Any]]]:
        return self.loader.get_historical_prices_for_funds(
            list(fund_pool),
            int(start_date.replace("-", "")),
            int(end_date.replace("-", "")),
        )

    def market_data(self, fund_pool: Sequence[str], current_date: int) -> dict[str, dict[str, Any]]:
        return self.loader.get_price_data(list(fund_pool), current_date)

    def news(
        self,
        sources: Sequence[str],
        current_date: int,
        top_rank: int,
        pre_k_days: int,
    ) -> tuple[Mapping[str, Any], ...]:
        if self.same_day_news_policy == "disabled":
            return ()
        raw = self.loader.get_news(list(sources), current_date, top_rank=top_rank, pre_k_days=pre_k_days)
        if self.same_day_news_policy == "previous_day_only":
            current_iso = _format_date(current_date)
            filtered = []
            for item in raw:
                item_date = str(item.get("THEDATE") or item.get("date") or "")
                if item_date and item_date[:10] >= current_iso:
                    continue
                filtered.append(item)
            return tuple(filtered)
        if self.same_day_news_policy != "official_available":
            raise ValueError(
                "same_day_news_policy must be previous_day_only, official_available, or disabled"
            )
        return tuple(raw)
