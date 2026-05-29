"""Small table-generation helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable


def flatten_result_row(result: dict[str, Any]) -> dict[str, Any]:
    experiment = result.get("experiment", {})
    row = {
        "name": result.get("run_name") or experiment.get("name"),
        "run_id": experiment.get("run_id"),
        "config_hash": experiment.get("config_hash"),
        "agent_name": experiment.get("agent_name"),
        "group": experiment.get("group"),
        "ablation": experiment.get("ablation"),
        "track": result.get("track"),
        "final_value": result.get("final_value"),
    }
    row.update(result.get("metrics", {}))
    return row


def add_baseline_deltas(rows: Iterable[dict[str, Any]], *, baseline_name: str = "s1_macro") -> list[dict[str, Any]]:
    materialized = [dict(row) for row in rows]
    baseline = next((row for row in materialized if row.get("name") == baseline_name), None)
    if not baseline:
        return materialized
    baseline_return = _as_float(baseline.get("cumulative_return"))
    baseline_sharpe = _as_float(baseline.get("sharpe_ratio"))
    for row in materialized:
        row["delta_cumulative_return_vs_s1"] = _delta(_as_float(row.get("cumulative_return")), baseline_return)
        row["delta_sharpe_vs_s1"] = _delta(_as_float(row.get("sharpe_ratio")), baseline_sharpe)
    return materialized


def markdown_table(rows: Iterable[dict[str, Any]], columns: list[str]) -> str:
    materialized = list(rows)
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in materialized
    ]
    return "\n".join([header, divider, *body])


def write_csv_table(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})
    return path


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _delta(value: float | None, baseline: float | None) -> float | None:
    if value is None or baseline is None:
        return None
    return value - baseline
