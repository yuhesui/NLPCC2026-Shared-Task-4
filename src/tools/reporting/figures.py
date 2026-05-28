"""Dependency-free figure placeholders for reports."""

from __future__ import annotations

from pathlib import Path


SPARKLINE_CHARS = "._-=+*#"


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    low = min(values)
    high = max(values)
    if high == low:
        return SPARKLINE_CHARS[0] * len(values)
    scale = len(SPARKLINE_CHARS) - 1
    return "".join(SPARKLINE_CHARS[round(((value - low) / (high - low)) * scale)] for value in values)


def write_equity_sparkline(path: Path, portfolio_history: list[dict]) -> Path:
    values = [float(row["total_value"]) for row in portfolio_history]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sparkline(values), encoding="utf-8")
    return path
