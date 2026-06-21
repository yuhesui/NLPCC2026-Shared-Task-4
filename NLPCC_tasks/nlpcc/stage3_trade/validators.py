"""Stage 3 leakage and input validators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FORBIDDEN_CURRENT_FIELDS = frozenset({"close", "high", "low", "change", "pctchange", "pct_change", "return"})


class Stage3ValidationError(ValueError):
    """Raised when Stage 3 input cannot be used safely."""


@dataclass(frozen=True)
class Stage3ValidationIssue:
    code: str
    message: str
    fund_id: str | None = None
    date_int: int | None = None


def _date_int(row: dict[str, Any]) -> int | None:
    value = row.get("date_int", row.get("date"))
    if value in (None, ""):
        return None
    return int(str(value).replace("-", "")[:8])


def find_price_input_issues(
    historical_prices: dict[str, list[dict[str, Any]]],
    decision_date: int,
) -> list[Stage3ValidationIssue]:
    issues: list[Stage3ValidationIssue] = []
    for fund_id, rows in historical_prices.items():
        for row in rows:
            row_date = _date_int(row)
            if row_date is None:
                issues.append(Stage3ValidationIssue("missing_date", "Price row is missing a date.", fund_id=fund_id))
                continue
            if row_date > decision_date:
                issues.append(
                    Stage3ValidationIssue(
                        "future_price_bar",
                        "Price row date is after the decision date.",
                        fund_id=fund_id,
                        date_int=row_date,
                    )
                )
            if row_date == decision_date:
                populated = sorted(
                    field
                    for field in FORBIDDEN_CURRENT_FIELDS
                    if field in row and row.get(field) not in (None, "")
                )
                if populated:
                    issues.append(
                        Stage3ValidationIssue(
                            "current_day_price_leakage",
                            f"Current-day row exposes forbidden fields: {populated}.",
                            fund_id=fund_id,
                            date_int=row_date,
                        )
                    )
    return issues


def assert_safe_price_inputs(historical_prices: dict[str, list[dict[str, Any]]], decision_date: int) -> None:
    issues = find_price_input_issues(historical_prices, decision_date)
    if issues:
        joined = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise Stage3ValidationError(joined)
