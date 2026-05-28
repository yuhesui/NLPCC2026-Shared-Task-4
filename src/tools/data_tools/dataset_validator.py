"""Validation helpers for local smoke data."""

from __future__ import annotations

import csv
from pathlib import Path


REQUIRED_PRICE_COLUMNS = {"date", "open", "high", "low", "close"}
REQUIRED_NEWS_COLUMNS = {"THEDATE", "PUBLISH_TIME", "TITLE", "RANKING"}


def validate_csv_columns(path: Path, required_columns: set[str]) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = set(next(reader, []))
    return sorted(required_columns - header)


def validate_smoke_dataset(root: Path) -> dict[str, object]:
    price_path = root / "price_data" / "000300.SH.csv"
    news_path = root / "news_data" / "caixin_daily_dedup.csv"
    missing_paths = [str(path) for path in (price_path, news_path) if not path.exists()]
    missing_columns = {
        "price": validate_csv_columns(price_path, REQUIRED_PRICE_COLUMNS) if price_path.exists() else [],
        "news": validate_csv_columns(news_path, REQUIRED_NEWS_COLUMNS) if news_path.exists() else [],
    }
    return {
        "ok": not missing_paths and not missing_columns["price"] and not missing_columns["news"],
        "missing_paths": missing_paths,
        "missing_columns": missing_columns,
    }
