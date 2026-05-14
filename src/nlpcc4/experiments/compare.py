"""Run-comparison helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_run_metrics(run_dir: str | Path) -> list[dict[str, Any]]:
    """Load metrics.json from child run directories."""
    root = Path(run_dir)
    rows: list[dict[str, Any]] = []
    for metrics_path in sorted(root.glob("*/metrics.json")):
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        data["run_id"] = metrics_path.parent.name
        rows.append(data)
    return rows


def compare_metric(run_dir: str | Path, metric: str = "annualized_sharpe") -> list[dict[str, Any]]:
    """Return loaded runs sorted by a metric descending."""
    return sorted(load_run_metrics(run_dir), key=lambda item: float(item.get(metric, 0.0)), reverse=True)


def compare_runs() -> None:
    """Compatibility entry point used by earlier tests."""
    return None
