from nlpcc4.execution.turnover import apply_no_trade_band, apply_turnover_cap, estimate_turnover


def test_turnover_estimate_one_way():
    assert estimate_turnover({"a": 0.5}, {"b": 0.5}) == 0.5


def test_turnover_cap_scales_delta():
    capped = apply_turnover_cap({"a": 1.0, "b": 0.0}, {"a": 0.0, "b": 1.0}, 0.25)
    assert estimate_turnover({"a": 1.0, "b": 0.0}, capped) <= 0.25 + 1e-12


def test_no_trade_band_keeps_small_moves():
    adjusted = apply_no_trade_band({"a": 0.5}, {"a": 0.51}, 0.02)
    assert adjusted["a"] == 0.5
