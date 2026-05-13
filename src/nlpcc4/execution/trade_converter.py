"""Target-weight to official-trade conversion contract.

Strategies must return target weights first. This module is the only intended
place for converting those targets into official buy/sell API payloads.
"""

from dataclasses import dataclass, field
from typing import Mapping

from nlpcc4.execution.target_weights import validate_target_weights


@dataclass(frozen=True)
class TradeConversionRequest:
    """Inputs required to convert target weights into official trade actions."""

    target_weights: Mapping[str, float]
    current_weights: Mapping[str, float]
    portfolio_value: float
    cash: float
    no_trade_band: float = 0.0
    max_turnover: float | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)


def convert_target_weights_to_trades(request: TradeConversionRequest) -> list[dict]:
    """Convert target weights to official trade payloads.

    This is intentionally not implemented in the init phase. The implementation
    must read the official buy/sell semantics in `NLPCC_tasks` before producing
    API payloads.
    """
    validate_target_weights(request.target_weights)
    raise NotImplementedError("Trade conversion is planned for the S0/S1 phase.")
