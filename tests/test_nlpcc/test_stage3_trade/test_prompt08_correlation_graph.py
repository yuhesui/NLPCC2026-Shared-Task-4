from nlpcc.stage3_trade.models.correlation_graph import build_correlation_graph, pearson_correlation
from nlpcc.stage3_trade.pipeline import build_stage3_state


def test_correlation_graph_is_deterministic_from_prior_returns() -> None:
    returns = {
        "A": (0.01, 0.02, -0.01, 0.03),
        "B": (0.011, 0.021, -0.009, 0.029),
        "C": (-0.02, 0.01, 0.02, -0.01),
    }

    edges = build_correlation_graph(returns, threshold=0.8)

    assert pearson_correlation(returns["A"], returns["B"]) > 0.99
    assert edges == build_correlation_graph(returns, threshold=0.8)
    assert any(edge.left == "A" and edge.right == "B" for edge in edges)


def test_stage3_state_includes_correlation_graph_without_current_close() -> None:
    prices = {
        "A": [
            {"date_int": 20250102, "open": 10.0, "close": 10.0, "high": 10.1, "low": 9.9},
            {"date_int": 20250103, "open": 10.1, "close": 10.2, "high": 10.3, "low": 10.0},
            {"date_int": 20250106, "open": 10.3, "close": 10.1, "high": 10.4, "low": 10.0},
            {"date_int": 20250107, "open": 10.2, "close": None, "high": None, "low": None},
        ],
        "B": [
            {"date_int": 20250102, "open": 20.0, "close": 20.0, "high": 20.1, "low": 19.9},
            {"date_int": 20250103, "open": 20.1, "close": 20.4, "high": 20.5, "low": 20.0},
            {"date_int": 20250106, "open": 20.4, "close": 20.2, "high": 20.6, "low": 20.1},
            {"date_int": 20250107, "open": 20.2, "close": None, "high": None, "low": None},
        ],
    }

    state = build_stage3_state(historical_prices=prices, fund_pool=("A", "B"), decision_date=20250107)

    assert state.diagnostics["uses_current_day_fields"] == ["open"]
    assert state.correlation_graph
