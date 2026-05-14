from nlpcc4.common.types import DecisionContext
from nlpcc4.execution.turnover import estimate_turnover
from nlpcc4.strategies.track1_macro.s1_quant_core import Track1S1QuantCore
from nlpcc4.strategies.track1_macro.universe import TRACK1_UNIVERSE
from nlpcc4.strategies.track2_sector.s1_quant_core import Track2S1QuantCore
from nlpcc4.strategies.track2_sector.universe import TRACK2_UNIVERSE


def _history(assets, days=80):
    return {
        asset: [
            {
                "date": "2024-01-01",
                "date_int": 20240101 + i,
                "close": 100 + i * (idx + 1) * 0.1,
                "pct_change": 0.05 * (idx + 1),
            }
            for i in range(days)
        ]
        + [{"date": "2024-05-01", "date_int": 20240501, "open": 120, "close": None, "high": None, "low": None, "pct_change": None}]
        for idx, asset in enumerate(assets)
    }


def test_track1_s1_respects_weight_and_turnover_constraints():
    assets = TRACK1_UNIVERSE
    config = {
        "signals": {"momentum_windows": [5, 20], "volatility_window": 20},
        "portfolio": {"cash_buffer": 0.01, "max_single_weight": 0.30, "max_daily_turnover": 0.20, "no_trade_band": 0.0},
        "risk": {},
        "execution": {"max_daily_turnover": 0.20, "no_trade_band": 0.0},
    }
    context = DecisionContext("2024-05-01", "track1", assets, _history(assets), previous_weights={asset: 0.0 for asset in assets})
    output = Track1S1QuantCore(config).compute_target_weights(context)
    assert sum(output.target_weights.values()) <= 1.0
    assert max(output.target_weights.values()) <= 0.30 + 1e-12
    assert estimate_turnover({asset: 0.0 for asset in assets}, output.target_weights) <= 0.20 + 1e-12
    assert all(asset in assets for asset in output.target_weights)


def test_track2_s1_uses_only_track2_assets():
    assets = TRACK2_UNIVERSE
    config = {
        "signals": {"momentum_window": 20, "top_k": 4},
        "portfolio": {"cash_buffer": 0.01, "max_single_weight": 0.22, "max_daily_turnover": 0.20, "no_trade_band": 0.0},
        "execution": {"max_daily_turnover": 0.20, "no_trade_band": 0.0},
    }
    context = DecisionContext("2024-05-01", "track2", assets, _history(assets), previous_weights={asset: 0.0 for asset in assets})
    output = Track2S1QuantCore(config).compute_target_weights(context)
    assert set(output.target_weights) == set(assets)
    assert not any(asset in TRACK1_UNIVERSE for asset in output.target_weights)
