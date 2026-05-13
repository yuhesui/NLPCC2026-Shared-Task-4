"""Base contracts for custom strategies."""

from typing import Protocol

from nlpcc4.common.types import DecisionContext as StrategyContext
from nlpcc4.common.types import StrategyOutput as StrategyResult
from nlpcc4.execution.target_weights import validate_target_weights


class Strategy(Protocol):
    """Protocol implemented by all custom strategies."""

    name: str

    def compute_target_weights(self, context: StrategyContext) -> StrategyResult:
        """Return target weights using only leakage-safe context."""
        ...

__all__ = ["Strategy", "StrategyContext", "StrategyResult", "validate_target_weights"]
