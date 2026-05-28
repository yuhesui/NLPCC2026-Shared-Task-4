from pathlib import Path

from nlpcc.stage4_agent.models.s0_equal_weight_agent import S0EqualWeightAgent
from tools.backtesting.official_server_runner import OfficialServerRunner
from tools.backtesting.local_backtester import run_local_backtest
from tools.backtesting.replay import replay_file, replay_summary
from tools.backtesting.vectorized_backtester import (
    BatchBacktestSpec,
    run_equal_weight_matrix_backtest,
    run_vectorized_backtest,
)


def test_run_local_backtest_and_replay_summary() -> None:
    output_path = Path("outputs/test_tools_prompt04/backtesting/s0_smoke.json")
    result = run_local_backtest(
        data_root=Path("data/sample/smoke_test"),
        track="macro",
        agent=S0EqualWeightAgent(max_weight=1.0),
        output_path=output_path,
        lookback_days=2,
        load_news=False,
    )

    summary = replay_summary(result)
    file_summary = replay_file(output_path)

    assert result["status"] == "ok"
    assert summary["transaction_count"] > 0
    assert file_summary["final_value"] == result["final_value"]


def test_batch_backtester_runs_specs_deterministically() -> None:
    specs = [
        BatchBacktestSpec(
            name="s0_macro",
            data_root=Path("data/sample/smoke_test"),
            track="macro",
        )
    ]

    results = run_vectorized_backtest(specs)

    assert [result["run_name"] for result in results] == ["s0_macro"]
    assert results[0]["status"] == "ok"
    assert results[0]["engine"] == "numpy_matrix"
    assert results[0]["final_value"] > 100000.0


def test_equal_weight_matrix_backtest_uses_numpy_engine() -> None:
    result = run_equal_weight_matrix_backtest(
        Path("data/sample/smoke_test"),
        "macro",
        invested_weight=0.98,
    )

    payload = result.as_dict()
    assert payload["engine"] == "numpy_matrix"
    assert payload["metrics"]["cumulative_return"] > 0


def test_official_server_runner_reports_startable_script() -> None:
    runner = OfficialServerRunner(repo_root=Path("."))
    startable = runner.can_start()

    assert startable["startable"] is True
    assert Path(startable["command"][1]).name == "start_server.py"
