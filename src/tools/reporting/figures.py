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


def write_metric_bar_chart(path: Path, rows: list[dict], *, metric: str, width: int = 40) -> Path:
    values = [(str(row.get("name", "")), float(row.get(metric, 0.0) or 0.0)) for row in rows]
    if not values:
        text = ""
    else:
        low = min(value for _, value in values)
        high = max(value for _, value in values)
        span = high - low
        lines = []
        for name, value in values:
            length = width if span == 0 else max(1, round(((value - low) / span) * width))
            lines.append(f"{name:32} | {'#' * length} {value:.6f}")
        text = "\n".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
