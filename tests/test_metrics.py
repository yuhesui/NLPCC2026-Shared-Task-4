from nlpcc4.metrics.drawdown import max_drawdown
from nlpcc4.metrics.performance import cumulative_return, estimate_cost_drag, summarize_performance
from nlpcc4.metrics.sharpe import annualized_sharpe, daily_returns


def test_metrics_hand_computed_small_example():
    curve = [100.0, 110.0, 99.0, 121.0]
    assert round(cumulative_return(curve), 6) == 0.21
    assert round(max_drawdown(curve), 6) == -0.1
    summary = summarize_performance(curve, turnovers=[0.1, 0.2], final_weights={"a": 0.5, "b": 0.5})
    assert summary["total_turnover"] == 0.30000000000000004
    assert summary["concentration"] == 0.5


def test_daily_returns_and_zero_volatility_sharpe_edges():
    assert [round(value, 6) for value in daily_returns([100.0, 110.0, 99.0])] == [0.1, -0.1]
    assert daily_returns([100.0, 0.0, 10.0]) == [-1.0]
    assert annualized_sharpe([0.01, 0.01, 0.01]) == 0.0
    assert annualized_sharpe([0.01]) == 0.0


def test_cost_drag_hand_computed():
    assert estimate_cost_drag([0.25, 0.75], friction=0.0001) == 0.0001
