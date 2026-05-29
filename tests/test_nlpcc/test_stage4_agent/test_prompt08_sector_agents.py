from nlpcc.stage4_agent.models.kg_moe_lite_agent import KGMoELiteAgent
from nlpcc.stage4_agent.models.sector_rotation_agent import SectorRotationAgent


def _sector_prices() -> dict[str, list[dict]]:
    return {
        "159995.SZ": [
            {"date_int": 20250102, "open": 10.0, "close": 10.0, "high": 10.1, "low": 9.9},
            {"date_int": 20250103, "open": 10.2, "close": 10.5, "high": 10.6, "low": 10.1},
            {"date_int": 20250106, "open": 10.6, "close": 10.9, "high": 11.0, "low": 10.4},
            {"date_int": 20250107, "open": 11.0, "close": None, "high": None, "low": None},
        ],
        "159819.SZ": [
            {"date_int": 20250102, "open": 20.0, "close": 20.0, "high": 20.1, "low": 19.9},
            {"date_int": 20250103, "open": 20.2, "close": 20.6, "high": 20.8, "low": 20.0},
            {"date_int": 20250106, "open": 20.7, "close": 21.2, "high": 21.4, "low": 20.6},
            {"date_int": 20250107, "open": 21.1, "close": None, "high": None, "low": None},
        ],
        "512800.SH": [
            {"date_int": 20250102, "open": 5.0, "close": 5.0, "high": 5.1, "low": 4.9},
            {"date_int": 20250103, "open": 5.0, "close": 4.95, "high": 5.05, "low": 4.9},
            {"date_int": 20250106, "open": 4.95, "close": 4.9, "high": 5.0, "low": 4.85},
            {"date_int": 20250107, "open": 4.9, "close": None, "high": None, "low": None},
        ],
        "512200.SH": [
            {"date_int": 20250102, "open": 3.0, "close": 3.0, "high": 3.1, "low": 2.9},
            {"date_int": 20250103, "open": 3.0, "close": 2.95, "high": 3.05, "low": 2.9},
            {"date_int": 20250106, "open": 2.95, "close": 2.9, "high": 3.0, "low": 2.85},
            {"date_int": 20250107, "open": 2.9, "close": None, "high": None, "low": None},
        ],
    }


def _sector_news() -> list[dict]:
    return [
        {
            "SOURCE": "toy",
            "TITLE": "AI semiconductor policy support lifts software demand",
            "CONTENT": "Subsidy support for artificial intelligence and chip companies.",
            "RANKING": "1",
            "THEDATE": "2025-01-07",
            "PUBLISH_TIME": "2025-01-07 14:30:00",
        }
    ]


def test_sector_rotation_agent_runs_and_records_ablation_flags() -> None:
    agent = SectorRotationAgent.from_config({"constraints": {"max_weight": 0.5, "cash_reserve": 0.03, "max_turnover": 0.6}})

    decision = agent.make_decision(
        track="sector",
        fund_pool=tuple(_sector_prices()),
        historical_prices=_sector_prices(),
        news=_sector_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert decision["metadata"]["agent"] == "sector_rotation"
    assert decision["metadata"]["fallback_used"] is False
    assert decision["metadata"]["sector_impact_count"] > 0
    assert decision["metadata"]["forbidden_current_fields_used"] == []
    assert max(decision["target_weights"].values()) <= 0.5 + 1e-8


def test_sector_rotation_ablation_modes_are_available() -> None:
    trend_only = SectorRotationAgent.from_config(
        {
            "use_news": False,
            "use_graph": False,
            "trend_weight": 1.0,
            "news_weight": 0.0,
            "graph_weight": 0.0,
            "constraints": {"max_weight": 0.5, "cash_reserve": 0.03},
        }
    )
    equal_sector = SectorRotationAgent.from_config(
        {
            "use_news": False,
            "use_graph": False,
            "use_trend": False,
            "equal_weight": 1.0,
            "constraints": {"max_weight": 0.5, "cash_reserve": 0.03},
        }
    )

    trend_decision = trend_only.make_decision(
        track="sector",
        fund_pool=tuple(_sector_prices()),
        historical_prices=_sector_prices(),
        news=[],
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )
    equal_decision = equal_sector.make_decision(
        track="sector",
        fund_pool=tuple(_sector_prices()),
        historical_prices=_sector_prices(),
        news=[],
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert trend_decision["metadata"]["ablation"]["use_news"] is False
    assert equal_decision["metadata"]["ablation"]["use_trend"] is False
    assert len(set(equal_decision["target_weights"].values())) == 1


def test_kg_moe_lite_agent_runs_with_deterministic_gates() -> None:
    agent = KGMoELiteAgent.from_config({"constraints": {"max_weight": 0.5, "cash_reserve": 0.03, "max_turnover": 0.6}})

    first = agent.make_decision(
        track="sector",
        fund_pool=tuple(_sector_prices()),
        historical_prices=_sector_prices(),
        news=_sector_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )
    second = agent.make_decision(
        track="sector",
        fund_pool=tuple(_sector_prices()),
        historical_prices=_sector_prices(),
        news=_sector_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert first["metadata"]["agent"] == "kg_moe_lite"
    assert first["metadata"]["expert_gates"] == second["metadata"]["expert_gates"]
    assert first["target_weights"] == second["target_weights"]
