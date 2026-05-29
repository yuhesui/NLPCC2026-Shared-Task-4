from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.runtime.fallback_manager import FallbackManager, FallbackPolicy, validate_decision
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


def _prices() -> dict[str, list[dict]]:
    return {
        "000300.SH": [
            {"date_int": 20250102, "open": 10.0, "close": 10.0, "high": 10.1, "low": 9.9},
            {"date_int": 20250103, "open": 10.1, "close": 10.2, "high": 10.3, "low": 10.0},
            {"date_int": 20250106, "open": 10.2, "close": None, "high": None, "low": None},
        ],
        "000905.SH": [
            {"date_int": 20250102, "open": 20.0, "close": 20.0, "high": 20.1, "low": 19.9},
            {"date_int": 20250103, "open": 20.2, "close": 20.0, "high": 20.3, "low": 19.8},
            {"date_int": 20250106, "open": 20.1, "close": None, "high": None, "low": None},
        ],
    }


def test_validate_decision_flags_invalid_weights_and_high_turnover() -> None:
    policy = FallbackPolicy(
        constraints=PortfolioConstraints(max_weight=0.6, cash_reserve=0.03),
        max_allowed_turnover=0.05,
    )
    decision = {
        "target_weights": {"000300.SH": 0.70, "000905.SH": 0.20},
        "metadata": {"forbidden_current_fields_used": []},
    }

    result = validate_decision(
        decision,
        current_portfolio={"cash": 100000.0, "holdings": {}},
        historical_prices=_prices(),
        fund_pool=("000300.SH", "000905.SH"),
        policy=policy,
    )

    assert result.valid is False
    assert "invalid_weights" in result.triggers
    assert "high_turnover" in result.triggers


def test_fallback_manager_records_module_exception_in_trace() -> None:
    policy = FallbackPolicy(
        constraints=PortfolioConstraints(max_weight=0.7, cash_reserve=0.03),
        max_allowed_turnover=0.6,
    )
    fallback = S1QuantCoreAgent.from_config({"track": "macro", "max_weight": 0.7}).make_decision

    def _bad_primary(**kwargs):
        raise RuntimeError("boom")

    decision = FallbackManager(policy).run_with_fallback(
        source_agent_name="bad_agent",
        primary=_bad_primary,
        fallback=fallback,
        track="macro",
        fund_pool=("000300.SH", "000905.SH"),
        historical_prices=_prices(),
        news=[],
        current_portfolio={"cash": 100000.0, "holdings": {}},
        decision_date=20250106,
    )

    trace = decision["metadata"]["decision_trace"]
    assert decision["metadata"]["fallback_used"] is True
    assert trace["fallback_events"][0]["trigger"] == "module_exception"
    assert "RuntimeError:boom" in trace["fallback_events"][0]["reason"]


def test_fallback_manager_records_missing_dependency() -> None:
    policy = FallbackPolicy(
        constraints=PortfolioConstraints(max_weight=0.7, cash_reserve=0.03),
        max_allowed_turnover=0.6,
        required_dependencies=("definitely_missing_pkg_prompt09_xyz",),
    )
    fallback = S1QuantCoreAgent.from_config({"track": "macro", "max_weight": 0.7}).make_decision

    decision = FallbackManager(policy).run_with_fallback(
        source_agent_name="dependency_sensitive_agent",
        primary=fallback,
        fallback=fallback,
        track="macro",
        fund_pool=("000300.SH", "000905.SH"),
        historical_prices=_prices(),
        news=[],
        current_portfolio={"cash": 100000.0, "holdings": {}},
        decision_date=20250106,
    )

    event = decision["metadata"]["decision_trace"]["fallback_events"][0]
    assert event["trigger"] == "missing_dependency"
    assert "definitely_missing_pkg_prompt09_xyz" in event["reason"]
