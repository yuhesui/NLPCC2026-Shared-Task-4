"""Markdown/CSV reports from registry records, with baseline deltas."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

METRICS = ("cumulative_return", "sharpe_ratio", "maximum_drawdown", "turnover")


def markdown_table(records: Sequence[dict[str, Any]], *, baseline_id: str | None = None) -> str:
    base = next((r for r in records if r["experiment_id"] == baseline_id), None)
    head = "| experiment | grade | CR | Sharpe | MDD | Turnover |" + (" ΔCR | ΔSharpe |" if base else "")
    sep = "|---|---|---:|---:|---:|---:|" + ("---:|---:|" if base else "")
    lines = [head, sep]
    for r in records:
        m = r["metrics"]
        row = (f"| {r['experiment_id']} | {r['evidence_grade']} | {m['cumulative_return']:.4%} | {m['sharpe_ratio']:.2f} "
               f"| {m['maximum_drawdown']:.4%} | {m['turnover']:.4f} |")
        if base:
            bm = base["metrics"]
            row += f" {m['cumulative_return'] - bm['cumulative_return']:+.4%} | {m['sharpe_ratio'] - bm['sharpe_ratio']:+.2f} |"
        lines.append(row)
    if any(r["evidence_grade"] == "synthetic_plumbing" for r in records):
        lines.append("\n> Rows graded `synthetic_plumbing` ran on synthetic data: they verify code paths, not strategy value.")
    return "\n".join(lines)
