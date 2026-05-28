"""Small table-generation helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable


def flatten_result_row(result: dict[str, Any]) -> dict[str, Any]:
    row = {
        "name": result.get("run_name") or result.get("experiment", {}).get("name"),
        "track": result.get("track"),
        "final_value": result.get("final_value"),
    }
    row.update(result.get("metrics", {}))
    return row


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
