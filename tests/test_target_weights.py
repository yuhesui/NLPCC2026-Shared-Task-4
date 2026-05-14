import pytest

from nlpcc4.execution.target_weights import normalize_target_weights, validate_target_weights


def test_target_weights_validate_cash_residual():
    validate_target_weights({"a": 0.4, "b": 0.2})


def test_target_weights_reject_negative_and_overallocated():
    with pytest.raises(ValueError):
        validate_target_weights({"a": -0.01})
    with pytest.raises(ValueError):
        validate_target_weights({"a": 0.7, "b": 0.4})


def test_normalize_target_weights_respects_target_sum():
    weights = normalize_target_weights({"a": 2.0, "b": 1.0}, target_sum=0.9)
    assert round(sum(weights.values()), 12) == 0.9
    assert weights["a"] > weights["b"]
