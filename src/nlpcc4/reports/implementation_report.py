"""Small markdown report helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def render_run_report(run_id: str, metrics: Mapping[str, Any], diagnostics: Mapping[str, Any] | None = None) -> str:
    """Render a compact implementation/run report."""
    diagnostics = diagnostics or {}
    lines = [
        f"# Implementation Report: {run_id}",
        "",
        "## Metrics",
        "",
    ]
    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Diagnostics", ""])
    for key, value in diagnostics.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def write_run_report(path: str | Path, run_id: str, metrics: Mapping[str, Any], diagnostics: Mapping[str, Any] | None = None) -> Path:
    """Write a compact markdown report."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_run_report(run_id, metrics, diagnostics), encoding="utf-8", newline="\n")
    return output
