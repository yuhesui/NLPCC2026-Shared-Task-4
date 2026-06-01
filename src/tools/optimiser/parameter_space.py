"""Prompt16 strategy parameter-space catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.optimiser.search_space import SearchSpace


@dataclass(frozen=True)
class StrategyParameterSpace:
    strategy: str
    parameters: dict[str, tuple[Any, ...]]

    def as_search_space(self) -> SearchSpace:
        return SearchSpace.from_mapping(self.parameters)

    @property
    def combination_count(self) -> int:
        count = 1
        for values in self.parameters.values():
            count *= len(values)
        return count


def prompt16_default_parameter_spaces() -> dict[str, StrategyParameterSpace]:
    """Return bounded default spaces; full research grids can expand these."""

    return {
        "dro_bl_rp": StrategyParameterSpace(
            "dro_bl_rp",
            {
                "tau": (0.02, 0.05),
                "confidence_scale": (0.75, 1.0),
                "rp_anchor_weight": (0.2, 0.4),
                "turnover_cap": (0.2, 0.35),
                "max_weight": (0.30, 0.35),
            },
        ),
        "bsa_rp": StrategyParameterSpace(
            "bsa_rp",
            {
                "regime_decay": (0.90, 0.97),
                "risk_budget_floor": (0.02, 0.05),
                "belief_smoothing": (0.2, 0.4),
                "drawdown_throttle": (0.5, 0.8),
            },
        ),
        "armor_omd": StrategyParameterSpace(
            "armor_omd",
            {
                "eta": (0.05, 0.10),
                "expert_floor": (0.03, 0.05),
                "regret_decay": (0.90, 0.97),
                "transaction_penalty": (0.05, 0.10),
            },
        ),
        "leeqa_rank": StrategyParameterSpace(
            "leeqa_rank",
            {
                "momentum_weight": (0.4, 0.6),
                "news_weight": (0.2, 0.4),
                "top_k": (3, 5),
                "softmax_temperature": (0.5, 1.0),
                "turnover_cap": (0.25, 0.40),
            },
        ),
        "kg_moe_lite": StrategyParameterSpace(
            "kg_moe_lite",
            {
                "graph_decay": (0.85, 0.95),
                "router_temperature": (0.6, 1.0),
                "expert_weight_trend": (0.4, 0.6),
                "sector_cap": (0.25, 0.35),
            },
        ),
        "hgf_mpc": StrategyParameterSpace(
            "hgf_mpc",
            {
                "kalman_process_var": (0.0005, 0.001),
                "kalman_obs_var": (0.005, 0.01),
                "horizon": (1, 3),
                "turnover_penalty": (0.05, 0.10),
            },
        ),
        "ceva_kf_ciga": StrategyParameterSpace(
            "ceva_kf_ciga",
            {
                "stability_threshold": (0.10, 0.20),
                "causal_confidence_scale": (0.75, 1.0),
                "impact_decay": (0.85, 0.95),
                "overlay_weight": (0.15, 0.30),
            },
        ),
        "text_models": StrategyParameterSpace(
            "text_models",
            {
                "stage1_mode": ("rule_based", "bge_small_zh", "finbert_tone_chinese", "hybrid_rule_bge_finbert"),
                "sentiment_weight": (0.0, 0.25),
                "embedding_relevance_weight": (0.0, 0.25),
            },
        ),
    }


def total_combination_count(spaces: dict[str, StrategyParameterSpace] | None = None) -> int:
    selected = spaces or prompt16_default_parameter_spaces()
    return sum(space.combination_count for space in selected.values())
