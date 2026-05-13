import pytest

from nlpcc4.execution.trade_converter import (
    TradeConversionRequest,
    convert_target_weights_to_trades,
)


def test_trade_converter_stub_exists_and_is_not_implemented():
    request = TradeConversionRequest(
        target_weights={"000300.SH": 0.5},
        current_weights={"000300.SH": 0.0},
        portfolio_value=100000.0,
        cash=100000.0,
    )
    with pytest.raises(NotImplementedError):
        convert_target_weights_to_trades(request)
