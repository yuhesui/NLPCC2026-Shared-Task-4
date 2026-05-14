import pytest

from nlpcc4.llm.parsers import parse_json_object
from nlpcc4.llm.validators import validate_alpha_signal, validate_event_exposure_signal, validate_regime_signal


def test_parse_json_object_from_markdown_fence():
    parsed = parse_json_object('```json\n{"regime":"uncertain","confidence":0.1,"rationale":"","affected_assets":[]}\n```')
    assert parsed["regime"] == "uncertain"


def test_regime_schema_validation():
    signal = validate_regime_signal({"regime": "risk_on", "confidence": 0.8, "rationale": "x", "affected_assets": []})
    assert signal.regime == "risk_on"
    with pytest.raises(ValueError):
        validate_regime_signal({"regime": "bad", "confidence": 0.8})


def test_alpha_and_event_schema_validation():
    alpha = validate_alpha_signal({"as_of_date": "2024-01-02", "track": "track1", "scores": [], "overall_confidence": 0.0})
    event = validate_event_exposure_signal({"as_of_date": "2024-01-02", "events": [], "overall_confidence": 0.0})
    assert alpha.track == "track1"
    assert event.overall_confidence == 0.0
