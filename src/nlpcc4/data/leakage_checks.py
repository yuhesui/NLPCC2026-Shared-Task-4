"""No-future-data validation entry points."""

from __future__ import annotations

from typing import Mapping, Sequence


def validate_no_current_close_visible(
    historical_prices: Mapping[str, Sequence[Mapping]], decision_date_int: int | None = None
) -> None:
    """Assert current-day hidden fields are not visible in official-style history."""
    for asset, rows in historical_prices.items():
        if not rows:
            continue
        last = rows[-1]
        last_date = last.get("date_int")
        if decision_date_int is not None and last_date != decision_date_int:
            continue
        for field in ("close", "high", "low", "change", "pct_change"):
            if last.get(field) is not None:
                raise ValueError(f"future field {field} visible for {asset} on decision date")


def validate_no_future_dates(
    historical_prices: Mapping[str, Sequence[Mapping]], decision_date_int: int
) -> None:
    """Assert no price row after the decision date is visible."""
    for asset, rows in historical_prices.items():
        for row in rows:
            row_date = row.get("date_int")
            if row_date is not None and int(row_date) > decision_date_int:
                raise ValueError(f"future price row visible for {asset}: {row_date} > {decision_date_int}")


def run_leakage_checks(
    historical_prices: Mapping[str, Sequence[Mapping]], decision_date_int: int
) -> dict[str, object]:
    """Run all Phase 1a leakage checks and return diagnostics."""
    validate_no_future_dates(historical_prices, decision_date_int)
    validate_no_current_close_visible(historical_prices, decision_date_int)
    return {"passed": True, "decision_date_int": decision_date_int}
