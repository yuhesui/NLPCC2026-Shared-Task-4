from pathlib import Path

from tools.reporting.experiment_report import write_experiment_report_artifacts
from tools.reporting.tables import add_baseline_deltas, flatten_result_row


def _result(name: str, cumulative_return: float, sharpe: float) -> dict:
    return {
        "track": "macro",
        "final_value": 100000.0 * (1.0 + cumulative_return),
        "metrics": {
            "cumulative_return": cumulative_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": 0.01,
            "turnover": 0.02,
        },
        "experiment": {
            "name": name,
            "run_id": f"{name}_hash",
            "config_hash": "hash",
            "agent_name": name,
            "group": "baseline",
            "ablation": "base",
        },
        "portfolio_history": [{"total_value": 100000.0}, {"total_value": 100000.0 * (1.0 + cumulative_return)}],
    }


def test_baseline_deltas_compare_against_s1() -> None:
    rows = add_baseline_deltas([flatten_result_row(_result("s0_macro", 0.01, 0.5)), flatten_result_row(_result("s1_macro", 0.02, 0.7))])
    s0 = next(row for row in rows if row["name"] == "s0_macro")

    assert round(s0["delta_cumulative_return_vs_s1"], 6) == -0.01
    assert round(s0["delta_sharpe_vs_s1"], 6) == -0.2


def test_write_experiment_report_artifacts() -> None:
    root = Path("outputs/test_tools_prompt10/reporting")
    artifacts = write_experiment_report_artifacts(
        results=[_result("s0_macro", 0.01, 0.5), _result("s1_macro", 0.02, 0.7)],
        report_dir=root,
        title="Prompt10 Test",
    )

    assert Path(artifacts["summary_csv"]).exists()
    assert Path(artifacts["summary_md"]).exists()
    assert Path(artifacts["sharpe_chart"]).exists()
    assert Path(artifacts["return_chart"]).exists()
