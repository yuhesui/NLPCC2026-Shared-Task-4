from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent
from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent


def _prices() -> dict[str, list[dict]]:
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


def test_risk_parity_agent_runs_with_valid_weights() -> None:
    agent = RiskParityAgent.from_config(
        {"track": "macro", "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6}}
    )

    decision = agent.make_decision(
        track="macro",
        fund_pool=("000300.SH", "399006.SZ", "518880.SH"),
        historical_prices=_prices(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert decision["metadata"]["fallback_used"] is False
    assert decision["metadata"]["forbidden_current_fields_used"] == []
    assert sum(decision["target_weights"].values()) <= 0.97 + 1e-8
    assert max(decision["target_weights"].values()) <= 0.7 + 1e-8


def test_robust_bl_agent_uses_text_views_when_valid() -> None:
    agent = RobustBLAgent.from_config(
        {
            "track": "macro",
            "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6},
            "stage3": {"momentum_windows": [1, 2], "max_weight": 0.7},
        }
    )

    decision = agent.make_decision(
        track="macro",
        fund_pool=("000300.SH", "399006.SZ", "518880.SH"),
        historical_prices=_prices(),
        news=_news(),
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert decision["metadata"]["agent"] == "robust_bl"
    assert decision["metadata"]["fallback_used"] is False
    assert decision["metadata"]["bl_view_count"] >= 1
    assert decision["metadata"]["forbidden_current_fields_used"] == []


def test_robust_bl_agent_falls_back_to_s1_without_valid_views() -> None:
    agent = RobustBLAgent.from_config(
        {
            "track": "macro",
            "constraints": {"max_weight": 0.7, "cash_reserve": 0.03},
            "stage3": {"momentum_windows": [1, 2], "max_weight": 0.7},
        }
    )

    decision = agent.make_decision(
        track="macro",
        fund_pool=("000300.SH", "399006.SZ", "518880.SH"),
        historical_prices=_prices(),
        news=[],
        current_portfolio={"cash": 100000.0, "holdings": {}},
    )

    assert decision["metadata"]["agent"] == "robust_bl_fallback_s1"
    assert decision["metadata"]["fallback_used"] is True
    assert "no_valid_bl_views" in decision["metadata"]["fallback_reason"]
