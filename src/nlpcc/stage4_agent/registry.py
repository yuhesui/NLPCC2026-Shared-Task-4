"""Stage 4 agent registry."""

from __future__ import annotations

from collections.abc import Callable

from nlpcc.stage4_agent.models.armor_omd_agent import make_armor_omd_decision
from nlpcc.stage4_agent.models.bsa_rp_agent import make_bsa_rp_decision
from nlpcc.stage4_agent.models.ceva_kf_ciga_agent import make_ceva_kf_ciga_decision
from nlpcc.stage4_agent.models.conservative_ensemble_agent import make_conservative_ensemble_decision
from nlpcc.stage4_agent.models.dro_bl_rp_agent import make_dro_bl_rp_decision
from nlpcc.stage4_agent.models.hgf_mpc_agent import make_hgf_mpc_decision
from nlpcc.stage4_agent.models.kg_moe_lite_agent import make_kg_moe_lite_decision
from nlpcc.stage4_agent.models.leeqa_rank_agent import make_leeqa_rank_decision
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
    "dro_bl_rp": make_dro_bl_rp_decision,
    "bsa_rp": make_bsa_rp_decision,
    "armor_omd": make_armor_omd_decision,
    "leeqa_rank": make_leeqa_rank_decision,
    "sector_rotation": make_sector_rotation_decision,
    "kg_moe_lite": make_kg_moe_lite_decision,
    "hgf_mpc": make_hgf_mpc_decision,
    "ceva_kf_ciga": make_ceva_kf_ciga_decision,
    "conservative_ensemble": make_conservative_ensemble_decision,
    "oco_ensemble": make_oco_ensemble_decision,
}


def get_stage4_agent(name: str) -> Callable[..., dict]:
    try:
        return STAGE4_AGENT_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(STAGE4_AGENT_REGISTRY))
        raise KeyError(f"Unknown Stage 4 agent '{name}'. Available: {available}") from exc
