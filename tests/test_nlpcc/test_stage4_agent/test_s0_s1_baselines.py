from pathlib import Path

import pytest

from nlpcc.stage3_trade.validators import Stage3ValidationError
from nlpcc.stage4_agent.models.s0_equal_weight_agent import S0EqualWeightAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from tools.backtesting.local_backtester import LocalSmokeBacktester


def _prices() -> dict[str, list[dict]]:
    return {
        "000300.SH": [
            {"date_int": 20250102, "open": 10.0, "close": 10.0, "high": 10.1, "low": 9.9},
            {"date_int": 20250103, "open": 10.1, "close": 10.4, "high": 10.5, "low": 10.0},
            {"date_int": 20250106, "open": 10.5, "close": None, "high": None, "low": None},
        ],
        "000905.SH": [
            {"date_int": 20250102, "open": 20.0, "close": 20.0, "high": 20.1, "low": 19.9},
            {"date_int": 20250103, "open": 20.1, "close": 19.8, "high": 20.2, "low": 19.6},
            {"date_int": 20250106, "open": 19.9, "close": None, "high": None, "low": None},
        ],
    }


def test_s0_equal_weight_ignores_poisoned_current_day_forbidden_fields() -> None:
    safe = _prices()
    poisoned = _prices()
    poisoned["000300.SH"][-1].update({"close": 9999.0, "high": 9999.0, "low": 0.01, "pctchange": 999.0})
    agent = S0EqualWeightAgent(max_weight=0.6)
    kwargs = {
        "track": "macro",
        "fund_pool": ("000300.SH", "000905.SH"),
        "current_portfolio": {"cash": 100000.0, "holdings": {}},
    }

    safe_decision = agent.make_decision(historical_prices=safe, **kwargs)
    poisoned_decision = agent.make_decision(historical_prices=poisoned, **kwargs)

    assert safe_decision["target_weights"] == poisoned_decision["target_weights"]
    assert safe_decision["trades"] == poisoned_decision["trades"]
    assert safe_decision["metadata"]["forbidden_current_fields_used"] == []


def test_s1_macro_and_sector_configs_instantiate() -> None:
    macro = S1QuantCoreAgent.from_config({"track": "macro", "stage3": {"momentum_windows": [1, 2]}})
    sector = S1QuantCoreAgent.from_config({"track": "sector", "stage3": {"momentum_windows": [1, 2]}})

    assert macro.config.track == "macro"
    assert sector.config.track == "sector"
    assert sector.config.sector_trend_weight > macro.config.sector_trend_weight


def test_s1_quant_core_runs_and_rejects_forbidden_current_day_fields() -> None:
    agent = S1QuantCoreAgent.from_config(
        {
            "track": "macro",
            "max_weight": 0.6,
            "stage3": {"momentum_windows": [1, 2], "max_weight": 0.6},
        }
    )

    decision = agent.make_decision(
        track="macro",
        fund_pool=("000300.SH", "000905.SH"),
        historical_prices=_prices(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert decision["trades"]
    assert decision["metadata"]["forbidden_current_fields_used"] == []

    poisoned = _prices()
    poisoned["000300.SH"][-1]["close"] = 9999.0
    with pytest.raises(Stage3ValidationError):
        agent.make_decision(
            track="macro",
            fund_pool=("000300.SH", "000905.SH"),
            historical_prices=poisoned,
            current_portfolio={"cash": 100000.0, "holdings": {}},
        )


def test_s0_and_s1_run_in_local_backtester_on_smoke_subset() -> None:
    data_root = Path("data") / "sample" / "smoke_test"

    s0_result = LocalSmokeBacktester(
        data_root=data_root,
        track="macro",
        agent=S0EqualWeightAgent(max_weight=1.0),
    ).run()
    s1_result = LocalSmokeBacktester(
        data_root=data_root,
        track="macro",
        agent=S1QuantCoreAgent.from_config({"track": "macro", "max_weight": 1.0, "stage3": {"max_weight": 1.0}}),
    ).run()

    assert s0_result["status"] == "ok"
    assert s1_result["status"] == "ok"
    assert s0_result["transactions"]
    assert s1_result["transactions"]
