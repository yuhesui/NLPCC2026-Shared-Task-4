import json
from pathlib import Path

from nlpcc.stage4_agent.models.smoke_one_unit_agent import SmokeOneUnitAgent
from tools.backtesting.local_backtester import LocalSmokeBacktester
from tools.data_tools.dataset_mirror import create_smoke_subset
from tools.data_tools.manifest_builder import inspect_csv


TEST_ROOT = Path("outputs") / "test_integration" / "prompt01"


def test_smoke_agent_ignores_forbidden_current_day_fields():
    agent = SmokeOneUnitAgent(notional=100.0)
    safe_prices = {
        "000300.SH": [
            {"date_int": 20250102, "open": 10.0, "close": 10.2, "high": 10.3, "low": 9.9},
            {"date_int": 20250103, "open": 10.2, "close": None, "high": None, "low": None, "pct_change": None},
        ]
    }
    poisoned_prices = {
        "000300.SH": [
            safe_prices["000300.SH"][0],
            {"date_int": 20250103, "open": 10.2, "close": 9999, "high": 9999, "low": 0.01, "pct_change": 999},
        ]
    }

    safe = agent.make_decision(
        track="macro",
        historical_prices=safe_prices,
        news=[{"TITLE": "read"}],
        current_portfolio={"cash": 100000, "holdings": {}},
    )
    poisoned = agent.make_decision(
        track="macro",
        historical_prices=poisoned_prices,
        news=[{"TITLE": "read"}],
        current_portfolio={"cash": 100000, "holdings": {}},
    )

    assert safe["trades"] == poisoned["trades"]
    assert safe["metadata"]["forbidden_current_fields_used"] == []


def test_local_smoke_backtester_runs_and_writes_output():
    data_root = TEST_ROOT / "smoke_data"
    output_path = TEST_ROOT / "local_smoke.json"
    create_smoke_subset(data_root)

    result = LocalSmokeBacktester(data_root=data_root, track="macro").run(output_path)

    assert result["status"] == "ok"
    assert result["transactions"]
    assert output_path.exists()
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["leakage_note"].startswith("Current-day close")


def test_manifest_builder_detects_lfs_pointer():
    source = Path("NLPCC_tasks") / "dataset" / "price_data" / "export_data" / "000300.SH.csv"
    inspection = inspect_csv(source)

    if inspection["is_lfs_pointer"]:
        assert inspection["blocker"]
    else:
        assert inspection["blocker"] is None
        assert inspection["row_count"] > 0
        assert "date" in inspection["columns"]
