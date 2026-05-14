from nlpcc4.common.types import DecisionContext
from nlpcc4.experiments.registry import build_strategy
from nlpcc4.strategies.track1_macro.universe import TRACK1_UNIVERSE


def _history(assets=TRACK1_UNIVERSE[:4], days=70):
    return {
        asset: [
            {
                "date": f"2024-01-{(i % 28) + 1:02d}",
                "date_int": 20240101 + i,
                "close": 100 + i + j,
                "pct_change": 0.1 + j * 0.01,
            }
            for i in range(days)
        ]
        + [{"date": "2024-04-15", "date_int": 20240415, "open": 120, "close": None, "high": None, "low": None, "pct_change": None}]
        for j, asset in enumerate(assets)
    }


def test_equal_inverse_momentum_random_baselines_emit_valid_weights():
    config = {"portfolio": {"cash_buffer": 0.01, "max_single_weight": 0.5}, "signals": {"random_seed": 1}}
    context = DecisionContext("2024-04-15", "track1", TRACK1_UNIVERSE[:4], _history())
    for name in ["s0_equal_weight", "s0_inverse_vol", "s0_momentum", "s0_random_constrained"]:
        output = build_strategy("track1", name, config).compute_target_weights(context)
        assert sum(output.target_weights.values()) <= 1.0
        assert all(value >= 0 for value in output.target_weights.values())
        assert output.diagnostics["selected_assets"]
