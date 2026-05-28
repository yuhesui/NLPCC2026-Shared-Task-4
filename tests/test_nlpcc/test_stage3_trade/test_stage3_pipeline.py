import pytest

from nlpcc.stage3_trade.models.cash_feasibility import plan_rebalance_trades
from nlpcc.stage3_trade.models.covariance import sample_covariance
from nlpcc.stage3_trade.models.inverse_volatility import inverse_volatility_weights
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.validators import Stage3ValidationError


def _safe_prices() -> dict[str, list[dict]]:
    return {
        "FUND_A": [
            {"date_int": 20250102, "open": 10.0, "close": 10.0, "high": 10.2, "low": 9.8},
            {"date_int": 20250103, "open": 10.1, "close": 10.5, "high": 10.6, "low": 10.0},
            {"date_int": 20250106, "open": 10.6, "close": None, "high": None, "low": None},
        ],
        "FUND_B": [
            {"date_int": 20250102, "open": 20.0, "close": 20.0, "high": 20.2, "low": 19.8},
            {"date_int": 20250103, "open": 19.9, "close": 19.0, "high": 20.0, "low": 18.8},
            {"date_int": 20250106, "open": 18.9, "close": None, "high": None, "low": None},
        ],
    }


def test_stage3_state_uses_prior_complete_bars_and_current_open_only() -> None:
    state = build_stage3_state(
        historical_prices=_safe_prices(),
        fund_pool=("FUND_A", "FUND_B"),
        decision_date=20250106,
        config={"momentum_windows": [1, 2], "max_weight": 0.6},
    )

    assert state.assets["FUND_A"].current_open == 10.6
    assert state.assets["FUND_A"].last_close == 10.5
    assert state.assets["FUND_A"].prior_returns == pytest.approx((0.05,))
    assert state.diagnostics["uses_current_day_fields"] == ["open"]
    assert set(state.covariance) == {"FUND_A", "FUND_B"}
    assert sum(state.inverse_volatility_weight.values()) <= 1.0


def test_stage3_rejects_forbidden_current_day_price_fields() -> None:
    prices = _safe_prices()
    prices["FUND_A"][-1]["close"] = 999.0

    with pytest.raises(Stage3ValidationError, match="current_day_price_leakage"):
        build_stage3_state(historical_prices=prices, fund_pool=("FUND_A", "FUND_B"), decision_date=20250106)


def test_inverse_volatility_and_covariance_features_are_deterministic() -> None:
    returns = {"A": [0.01, 0.02, -0.01], "B": [0.01, 0.01, 0.01]}

    weights = inverse_volatility_weights(returns)
    covariance = sample_covariance(returns)

    assert weights["B"] > weights["A"]
    assert covariance["A"]["A"] > 0
    assert covariance["B"]["B"] == pytest.approx(0.0)


def test_cash_feasibility_does_not_use_same_day_sales_for_buys() -> None:
    trades = plan_rebalance_trades(
        {"FUND_A": 0.0, "FUND_B": 0.9},
        {"cash": 10.0, "holdings": {"FUND_A": 100.0}},
        {"FUND_A": 10.0, "FUND_B": 20.0},
        cash_reserve=0.0,
        rebalance_threshold=0.0,
    )

    buys = [trade for trade in trades if trade["action"] == "buy"]
    sells = [trade for trade in trades if trade["action"] == "sell"]
    assert sells
    assert sum(float(trade["amount"]) for trade in buys) <= 10.0
