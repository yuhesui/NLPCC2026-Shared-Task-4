"""Track 1 S4 conservative wrapper.

S4 is mainly meaningful for Track 2 sector mapping. Track 1 keeps the same
target-weight contract and deliberately falls back to S1 for Phase 1a.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.strategies.track1_macro.s1_quant_core import Track1S1QuantCore


@dataclass
class Track1S4EventExposure:
    config: Mapping[str, Any]
    name: str = "s4_event_exposure"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        base = Track1S1QuantCore(self.config).compute_target_weights(context)
        diagnostics = dict(base.diagnostics)
        diagnostics.update(
            {
                "strategy": self.name,
                "fallback_strategy": "s1_quant_core",
                "fallback_reason": "track1_event_sector_mapping_not_meaningful_in_phase_1a",
            }
        )
        return StrategyOutput(base.target_weights, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track1S4EventExposure:
    return Track1S4EventExposure(config or {})
