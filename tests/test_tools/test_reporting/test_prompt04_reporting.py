from pathlib import Path

from tools.reporting.artifacts import write_json_artifact
from tools.reporting.figures import sparkline, write_equity_sparkline
from tools.reporting.report_builder import build_markdown_report, write_markdown_report
from tools.reporting.tables import flatten_result_row, markdown_table, write_csv_table


def test_reporting_helpers_write_artifacts() -> None:
    result = {
        "run_name": "s0",
        "track": "macro",
        "final_value": 101.0,
        "metrics": {"cumulative_return": 0.01, "sharpe_ratio": 1.0, "max_drawdown": 0.0, "turnover": 0.1},
        "portfolio_history": [{"total_value": 100.0}, {"total_value": 101.0}],
    }
    root = Path("outputs/test_tools_prompt04/reporting")

    row = flatten_result_row(result)
    table = markdown_table([row], ["name", "track", "final_value"])
    report = build_markdown_report([result], title="Prompt04")
    json_path = write_json_artifact(root / "result.json", result)
    csv_path = write_csv_table(root / "table.csv", [row], ["name", "track", "final_value"])
    fig_path = write_equity_sparkline(root / "equity.txt", result["portfolio_history"])
    report_path = write_markdown_report(root / "report.md", [result], title="Prompt04")

    assert "| s0 | macro | 101.0 |" in table
    assert "# Prompt04" in report
    assert sparkline([1.0, 2.0])
    assert json_path.exists()
    assert csv_path.exists()
    assert fig_path.exists()
    assert report_path.exists()
