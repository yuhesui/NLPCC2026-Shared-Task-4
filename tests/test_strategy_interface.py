import pytest

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.execution.target_weights import validate_target_weights


def test_strategy_output_holds_target_weights():
    output = StrategyOutput(target_weights={"000300.SH": 0.5})
    assert output.target_weights["000300.SH"] == 0.5


def test_target_weight_validation_rejects_overallocated_weights():
    with pytest.raises(ValueError):
        validate_target_weights({"a": 0.8, "b": 0.3})


def test_decision_context_is_leakage_safe_container():
    context = DecisionContext(
        decision_date="2025-01-02",
        track="track1",
        fund_pool=("000300.SH",),
        historical_prices={},
    )
    assert context.fund_pool == ("000300.SH",)
