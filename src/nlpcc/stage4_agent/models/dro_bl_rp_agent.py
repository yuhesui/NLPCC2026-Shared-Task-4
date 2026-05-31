"""DRO-BL-RP MVP agent.

This MVP reuses the robust Black-Litterman engine already present in the repo:
text-derived BL views and confidence, a risk-parity/S1 anchor, long-only
constraints, and turnover control.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent, RobustBLAgentConfig


@dataclass(frozen=True)
class DROBLRPAgent:
    config: RobustBLAgentConfig = field(default_factory=RobustBLAgentConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "DROBLRPAgent":
        return cls(RobustBLAgentConfig.from_mapping(values))

    def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        decision = RobustBLAgent(self.config).make_decision(**kwargs)
        metadata = dict(decision.get("metadata", {}) or {})
        metadata["agent"] = "dro_bl_rp"
        metadata["method_maturity"] = "functional_mvp"
        metadata["method_note"] = "Robust BL posterior with risk-parity/S1 anchor and turnover control."
        decision["metadata"] = metadata
        decision["reasoning"] = (
            "DRO-BL-RP MVP: robust Black-Litterman views plus risk-parity/S1 anchor, "
            "long-only caps, and turnover control."
        )
        return decision


def make_dro_bl_rp_decision(**kwargs: Any) -> dict[str, Any]:
    return DROBLRPAgent().make_decision(**kwargs)
