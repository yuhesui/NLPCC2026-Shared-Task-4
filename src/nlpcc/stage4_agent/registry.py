"""Stage 4 agent registry."""

from __future__ import annotations

from collections.abc import Callable

from nlpcc.stage4_agent.models.conservative_ensemble_agent import make_conservative_ensemble_decision
from nlpcc.stage4_agent.models.kg_moe_lite_agent import make_kg_moe_lite_decision
from nlpcc.stage4_agent.models.oco_ensemble_agent import make_oco_ensemble_decision
from nlpcc.stage4_agent.models.risk_parity_agent import make_risk_parity_decision
from nlpcc.stage4_agent.models.robust_bl_agent import make_robust_bl_decision
from nlpcc.stage4_agent.models.s0_equal_weight_agent import make_s0_decision
from nlpcc.stage4_agent.models.s1_quant_core import make_s1_decision
from nlpcc.stage4_agent.models.smoke_one_unit_agent import make_smoke_decision
from nlpcc.stage4_agent.models.sector_rotation_agent import make_sector_rotation_decision


STAGE4_AGENT_REGISTRY: dict[str, Callable[..., dict]] = {
    "smoke_one_unit": make_smoke_decision,
    "s0_equal_weight": make_s0_decision,
    "s1_quant_core": make_s1_decision,
    "risk_parity": make_risk_parity_decision,
    "robust_bl": make_robust_bl_decision,
    "sector_rotation": make_sector_rotation_decision,
    "kg_moe_lite": make_kg_moe_lite_decision,
    "conservative_ensemble": make_conservative_ensemble_decision,
    "oco_ensemble": make_oco_ensemble_decision,
}


def get_stage4_agent(name: str) -> Callable[..., dict]:
    try:
        return STAGE4_AGENT_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(STAGE4_AGENT_REGISTRY))
        raise KeyError(f"Unknown Stage 4 agent '{name}'. Available: {available}") from exc
