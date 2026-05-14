import pytest

from nlpcc4.common.types import DecisionContext
from nlpcc4.llm.manual_io import ManualLLMRequest, ManualResponseInvalid
from nlpcc4.strategies.track1_macro.s2_llm_regime import Track1S2LLMRegime
from nlpcc4.strategies.track1_macro.universe import TRACK1_UNIVERSE


def _history(assets):
    return {
        asset: [
            {"date": "2024-01-01", "date_int": 20240101 + i, "close": 100 + i, "pct_change": 0.1}
            for i in range(80)
        ]
        + [{"date": "2024-05-01", "date_int": 20240501, "open": 120, "close": None, "high": None, "low": None, "pct_change": None}]
        for asset in assets
    }


def test_s2_api_without_key_falls_back_to_s1(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = {
        "signals": {"momentum_windows": [5, 20], "volatility_window": 20},
        "portfolio": {"cash_buffer": 0.01, "max_single_weight": 0.30, "max_daily_turnover": 0.20, "no_trade_band": 0.0},
        "risk": {},
        "execution": {"max_daily_turnover": 0.20},
        "llm": {"mode": "api", "confidence_threshold": 0.55},
    }
    context = DecisionContext(
        "2024-05-01",
        "track1",
        TRACK1_UNIVERSE,
        _history(TRACK1_UNIVERSE),
        previous_weights={asset: 0.0 for asset in TRACK1_UNIVERSE},
        llm_mode="api",
        run_id="test_fallback",
    )
    output = Track1S2LLMRegime(config).compute_target_weights(context)
    assert output.diagnostics["fallback_reason"].startswith("llm_invalid_or_unavailable")


def test_s2_manual_invalid_json_is_rejected():
    run_id = "test_s2_manual_invalid_json_is_rejected"
    stem = "20240501_track1_s2_llm_regime_regime"
    request = ManualLLMRequest(run_id, stem, "")
    request.response_path.parent.mkdir(parents=True, exist_ok=True)
    request.response_path.write_text("{ invalid json", encoding="utf-8")
    config = {
        "signals": {"momentum_windows": [5, 20], "volatility_window": 20},
        "portfolio": {"cash_buffer": 0.01, "max_single_weight": 0.30, "max_daily_turnover": 0.20, "no_trade_band": 0.0},
        "risk": {},
        "execution": {"max_daily_turnover": 0.20},
        "llm": {"mode": "manual", "confidence_threshold": 0.55},
    }
    context = DecisionContext(
        "2024-05-01",
        "track1",
        TRACK1_UNIVERSE,
        _history(TRACK1_UNIVERSE),
        previous_weights={asset: 0.0 for asset in TRACK1_UNIVERSE},
        llm_mode="manual",
        run_id=run_id,
    )
    with pytest.raises(ManualResponseInvalid):
        Track1S2LLMRegime(config).compute_target_weights(context)
