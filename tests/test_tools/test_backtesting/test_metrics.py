import math

import pytest

from tools.backtesting.metrics import (
    annualized_volatility,
    compute_backtest_metrics,
    cumulative_return,
    daily_returns,
    max_drawdown,
    transaction_turnover,
    weight_turnover,
)


def test_daily_and_cumulative_returns() -> None:
    values = [100.0, 110.0, 99.0]

    assert daily_returns(values) == pytest.approx([0.10, -0.10])
    assert cumulative_return(values) == pytest.approx(-0.01)


def test_annualized_volatility_uses_sample_standard_deviation() -> None:
    returns = [0.10, -0.10]

    expected_sample_std = math.sqrt(0.02)

    assert annualized_volatility(returns, periods_per_year=1) == pytest.approx(expected_sample_std)


def test_max_drawdown_reports_peak_to_trough_loss() -> None:
    assert max_drawdown([100.0, 120.0, 90.0, 95.0]) == pytest.approx(0.25)


def test_weight_turnover_is_average_one_way_turnover() -> None:
    history = [
        {"FUND_A": 1.0},
        {"FUND_A": 0.5, "FUND_B": 0.5},
        {"FUND_B": 1.0},
    ]

    assert weight_turnover(history) == pytest.approx(0.5)


def test_transaction_turnover_uses_average_portfolio_value() -> None:
    transactions = [{"fund_id": "FUND_A", "amount": 100.0}, {"fund_id": "FUND_A", "amount_sold": 50.0}]

    assert transaction_turnover(transactions, [1000.0, 1100.0, 900.0]) == pytest.approx(0.15)


def test_compute_backtest_metrics_returns_required_fields() -> None:
    metrics = compute_backtest_metrics(
        [100.0, 101.0, 100.0, 103.0],
        weight_history=[{"FUND_A": 1.0}, {"FUND_A": 0.5, "FUND_B": 0.5}],
    )

    values = metrics.as_dict()
    assert set(values) == {
        "cumulative_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "turnover",
    }
    assert values["cumulative_return"] == pytest.approx(0.03)
    assert values["turnover"] == pytest.approx(0.5)
