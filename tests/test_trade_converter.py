from nlpcc4.execution.trade_converter import TradeConversionRequest, convert_target_weights_to_trades


def test_trade_converter_emits_official_buy_amount_and_sell_percentage():
    request = TradeConversionRequest(
        target_weights={"000300.SH": 0.2, "518880.SH": 0.3},
        current_weights={"000300.SH": 0.5, "518880.SH": 0.0},
        current_values={"000300.SH": 50000.0, "518880.SH": 0.0},
        portfolio_value=100000.0,
        cash=50000.0,
    )
    trades = convert_target_weights_to_trades(request)
    assert {"fund_id": "000300.SH", "action": "sell", "percentage": 0.6} in trades
    assert {"fund_id": "518880.SH", "action": "buy", "amount": 30000.0} in trades


def test_trade_converter_does_not_use_future_sell_proceeds_for_buys():
    request = TradeConversionRequest(
        target_weights={"a": 0.0, "b": 1.0},
        current_weights={"a": 1.0, "b": 0.0},
        current_values={"a": 100000.0, "b": 0.0},
        portfolio_value=100000.0,
        cash=0.0,
    )
    trades = convert_target_weights_to_trades(request)
    assert any(t["action"] == "sell" for t in trades)
    assert not any(t["action"] == "buy" for t in trades)


def test_trade_converter_handles_zero_value_and_tiny_differences():
    zero_value = TradeConversionRequest(
        target_weights={"a": 0.5},
        current_weights={"a": 0.0},
        portfolio_value=0.0,
        cash=0.0,
    )
    assert convert_target_weights_to_trades(zero_value) == []

    tiny_difference = TradeConversionRequest(
        target_weights={"a": 0.500000001},
        current_weights={"a": 0.5},
        current_values={"a": 50000.0},
        portfolio_value=100000.0,
        cash=50000.0,
        no_trade_band=0.01,
    )
    assert convert_target_weights_to_trades(tiny_difference) == []


def test_trade_converter_scales_buys_to_cash_after_buffer():
    request = TradeConversionRequest(
        target_weights={"a": 0.4, "b": 0.4},
        current_weights={"a": 0.0, "b": 0.0},
        portfolio_value=100000.0,
        cash=50000.0,
        cash_buffer=0.1,
    )
    buys = [trade for trade in convert_target_weights_to_trades(request) if trade["action"] == "buy"]
    assert round(sum(trade["amount"] for trade in buys), 6) == 40000.0
