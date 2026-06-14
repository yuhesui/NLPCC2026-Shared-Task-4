"""Synthetic manifest validators."""

from __future__ import annotations


REQUIRED_MANIFEST_FIELDS = {
    "source_years",
    "random_seed",
    "scenario_name",
    "date_range",
    "rows",
    "assets",
    "news_count_before",
    "news_count_after",
    "price_count_before",
    "price_count_after",
    "leakage_checks_passed",
}


def validate_synthetic_manifest(row: dict[str, object]) -> list[str]:
    missing = sorted(field for field in REQUIRED_MANIFEST_FIELDS if field not in row)
    problems = [f"missing:{field}" for field in missing]
    if str(row.get("source_years", "")).find("2026") >= 0:
        problems.append("hidden_2026")
    if row.get("leakage_checks_passed") not in {True, "true", "True", "pass"}:
        problems.append("leakage_check_not_pass")
    return problems
