"""Experiment-suite report artifact generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.reporting.figures import write_equity_sparkline, write_metric_bar_chart
from tools.reporting.report_builder import DEFAULT_COLUMNS, write_markdown_report
from tools.reporting.tables import add_baseline_deltas, flatten_result_row, write_csv_table


def write_experiment_report_artifacts(
    *,
    results: list[dict[str, Any]],
    report_dir: Path,
    title: str,
) -> dict[str, str]:
    report_dir.mkdir(parents=True, exist_ok=True)
    rows = add_baseline_deltas([flatten_result_row(result) for result in results])
    artifacts = {
        "summary_csv": str(write_csv_table(report_dir / "ablation_summary.csv", rows, DEFAULT_COLUMNS)),
        "summary_md": str(write_markdown_report(report_dir / "ablation_report.md", results, title=title)),
        "sharpe_chart": str(write_metric_bar_chart(report_dir / "figures" / "sharpe_ratio.txt", rows, metric="sharpe_ratio")),
        "return_chart": str(
            write_metric_bar_chart(report_dir / "figures" / "cumulative_return.txt", rows, metric="cumulative_return")
        ),
    }
    for result in results:
        experiment = result.get("experiment", {})
        run_id = str(experiment.get("run_id") or experiment.get("name") or "run")
        artifacts[f"equity_{run_id}"] = str(
            write_equity_sparkline(report_dir / "figures" / f"{run_id}_equity.txt", result.get("portfolio_history", []))
        )
    return artifacts
