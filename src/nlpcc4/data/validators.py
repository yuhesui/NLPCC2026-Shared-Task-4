"""Validation helpers for market and news inputs."""

from __future__ import annotations

from typing import Mapping, Sequence


def validate_non_empty_fund_pool(fund_pool: Sequence[str]) -> None:
    """Validate that a strategy has at least one candidate fund."""
    if not fund_pool:
        raise ValueError("fund_pool must not be empty")
    if any(not str(asset).strip() for asset in fund_pool):
        raise ValueError("fund_pool contains an empty asset id")


def validate_date_range(start_date: str, end_date: str) -> None:
    """Validate ISO date strings for chronological runs."""
    if start_date > end_date:
        raise ValueError(f"start_date must be <= end_date: {start_date} > {end_date}")


def validate_price_panel(historical_prices: Mapping[str, Sequence[Mapping]]) -> None:
    """Validate the official-compatible price panel shape."""
    if not historical_prices:
        raise ValueError("historical_prices must not be empty")
    for asset, rows in historical_prices.items():
        if not asset:
            raise ValueError("price panel contains empty asset id")
        if not isinstance(rows, Sequence):
            raise ValueError(f"price rows for {asset} must be a sequence")
