from nlpcc.stage4_agent.models.conservative_ensemble_agent import ConservativeEnsembleAgent
from nlpcc.stage4_agent.models.oco_ensemble_agent import OCOEnsembleAgent
from nlpcc.stage4_agent.registry import get_stage4_agent


def _macro_prices() -> dict[str, list[dict]]:
    return {
        "000300.SH": [
            {"date_int": 20250102, "open": 10.0, "close": 10.0, "high": 10.1, "low": 9.9},
            {"date_int": 20250103, "open": 10.1, "close": 10.3, "high": 10.4, "low": 10.0},
            {"date_int": 20250106, "open": 10.4, "close": 10.2, "high": 10.5, "low": 10.1},
            {"date_int": 20250107, "open": 10.2, "close": None, "high": None, "low": None},
        ],
        "399006.SZ": [
            {"date_int": 20250102, "open": 20.0, "close": 20.0, "high": 20.2, "low": 19.8},
            {"date_int": 20250103, "open": 20.1, "close": 20.8, "high": 21.0, "low": 20.0},
            {"date_int": 20250106, "open": 20.7, "close": 21.5, "high": 21.8, "low": 20.6},
            {"date_int": 20250107, "open": 21.4, "close": None, "high": None, "low": None},
        ],
        "518880.SH": [
            {"date_int": 20250102, "open": 5.0, "close": 5.0, "high": 5.1, "low": 4.9},
            {"date_int": 20250103, "open": 5.1, "close": 5.05, "high": 5.2, "low": 5.0},
            {"date_int": 20250106, "open": 5.0, "close": 5.08, "high": 5.1, "low": 4.95},
            {"date_int": 20250107, "open": 5.1, "close": None, "high": None, "low": None},
        ],
    }


def _news() -> list[dict]:
    return [
        {
            "SOURCE": "toy",
            "TITLE": "Policy support boosts semiconductor and AI growth",
            "CONTENT": "State Council stimulus and subsidy support technology demand recovery.",
            "RANKING": "1",
            "THEDATE": "2025-01-07",
            "PUBLISH_TIME": "2025-01-07 14:30:00",
        }
    ]


def test_conservative_ensemble_runs_and_traces_valid_decision() -> None:
    agent = ConservativeEnsembleAgent.from_config(
        {
            "track": "macro",
            "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
            "fallback_policy": {
                "max_allowed_turnover": 0.6,
                "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
            },
        }
    )

    decision = agent.make_decision(
        track="macro",
        fund_pool=tuple(_macro_prices()),
        historical_prices=_macro_prices(),
        news=_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert decision["metadata"]["agent"] == "conservative_ensemble"
    assert decision["metadata"]["fallback_used"] is False
    assert decision["metadata"]["decision_trace"]["fallback_events"] == []
    assert set(decision["metadata"]["valid_child_agents"]) == {"s1_quant_core", "risk_parity"}
    assert decision["metadata"]["forbidden_current_fields_used"] == []
    assert max(decision["target_weights"].values()) <= 0.7 + 1e-8


def test_oco_ensemble_runs_with_deterministic_expert_gates() -> None:
    config = {
        "track": "macro",
        "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
        "fallback_policy": {
            "max_allowed_turnover": 0.6,
            "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
        },
        "experts": [
            {"name": "s1_quant_core", "prior_weight": 0.6, "config": {"max_weight": 0.7}},
            {
                "name": "risk_parity",
                "prior_weight": 0.4,
                "config": {"constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6}},
            },
        ],
    }
    agent = OCOEnsembleAgent.from_config(config)

    first = agent.make_decision(
        track="macro",
        fund_pool=tuple(_macro_prices()),
        historical_prices=_macro_prices(),
        news=_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )
    second = agent.make_decision(
        track="macro",
        fund_pool=tuple(_macro_prices()),
        historical_prices=_macro_prices(),
        news=_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert first["metadata"]["agent"] == "oco_ensemble"
    assert first["metadata"]["fallback_used"] is False
    assert first["metadata"]["expert_gates"] == second["metadata"]["expert_gates"]
    assert abs(sum(first["metadata"]["expert_gates"].values()) - 1.0) < 1e-12
    assert first["metadata"]["decision_trace"]["fallback_events"] == []


def test_oco_ensemble_falls_back_and_records_dependency_failure() -> None:
    agent = OCOEnsembleAgent.from_config(
        {
            "track": "macro",
            "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
            "fallback_policy": {
                "max_allowed_turnover": 0.6,
                "required_dependencies": ["definitely_missing_pkg_prompt09_abc"],
                "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
            },
        }
    )

    decision = agent.make_decision(
        track="macro",
        fund_pool=tuple(_macro_prices()),
        historical_prices=_macro_prices(),
        news=_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    event = decision["metadata"]["decision_trace"]["fallback_events"][0]
    assert decision["metadata"]["fallback_used"] is True
    assert event["trigger"] == "missing_dependency"
    assert "definitely_missing_pkg_prompt09_abc" in event["reason"]


def test_prompt09_agents_are_registered() -> None:
    assert get_stage4_agent("oco_ensemble")
    assert get_stage4_agent("conservative_ensemble")
