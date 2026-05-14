import json

import pytest

from nlpcc4.llm.manual_io import (
    ManualLLMRequest,
    ManualResponseInvalid,
    ManualResponseMissing,
    read_manual_response,
    write_manual_prompt,
)
from nlpcc4.llm.validators import validate_regime_signal


def test_manual_llm_request_response_round_trip():
    request = ManualLLMRequest("test_manual_round_trip", "20240102_track1_s2_llm_regime_regime", "Prompt")
    prompt_path = write_manual_prompt(request)
    assert prompt_path.exists()
    request.response_path.write_text(
        json.dumps({"regime": "uncertain", "confidence": 0.1, "rationale": "x", "affected_assets": []}),
        encoding="utf-8",
    )
    signal = read_manual_response(request, validate_regime_signal)
    assert signal.regime == "uncertain"


def test_manual_llm_missing_response_is_clear():
    request = ManualLLMRequest("test_manual_missing", "missing_response", "Prompt")
    write_manual_prompt(request)
    if request.response_path.exists():
        request.response_path.unlink()
    with pytest.raises(ManualResponseMissing) as exc:
        read_manual_response(request, validate_regime_signal)
    assert str(request.response_path) in str(exc.value)


def test_manual_llm_invalid_response_is_clear():
    request = ManualLLMRequest("test_manual_invalid", "invalid_response", "Prompt")
    write_manual_prompt(request)
    request.response_path.write_text("{ invalid json", encoding="utf-8")
    with pytest.raises(ManualResponseInvalid) as exc:
        read_manual_response(request, validate_regime_signal)
    assert str(request.response_path) in str(exc.value)
