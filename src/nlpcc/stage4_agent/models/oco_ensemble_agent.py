"""Online-convex-optimisation inspired deterministic ensemble agent."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.runtime.fallback_manager import FallbackManager, FallbackPolicy, validate_decision
from nlpcc.stage4_agent.ensemble_utils import blend_target_weights, build_weight_decision
from nlpcc.stage4_agent.models.conservative_ensemble_agent import ConservativeEnsembleAgent
from nlpcc.stage4_agent.models.kg_moe_lite_agent import KGMoELiteAgent
from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent
from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from nlpcc.stage4_agent.models.sector_rotation_agent import SectorRotationAgent


@dataclass(frozen=True)
class OCOExpertConfig:
    name: str
    prior_weight: float
    config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "OCOExpertConfig":
        data = dict(value)
        return cls(
            name=str(data.pop("name")),
            prior_weight=float(data.pop("prior_weight", 1.0)),
            config=dict(data.pop("config", {}) or {}),
        )


@dataclass(frozen=True)
class OCOEnsembleConfig:
    track: TrackName = "macro"
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    fallback_policy: FallbackPolicy = field(default_factory=lambda: FallbackPolicy(max_allowed_turnover=0.60))
    learning_rate: float = 0.8
    fallback_penalty: float = 0.5
    turnover_penalty: float = 0.2
    experts: tuple[OCOExpertConfig, ...] = ()

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "OCOEnsembleConfig":
        if not values:
            return cls()
        data = dict(values)
        constraints = PortfolioConstraints.from_mapping(data.pop("constraints", None))
        fallback_policy = FallbackPolicy.from_mapping(data.pop("fallback_policy", None))
        if "fallback_policy" not in values:
            fallback_policy = FallbackPolicy(constraints=constraints, max_allowed_turnover=0.60)
        experts = tuple(OCOExpertConfig.from_mapping(item) for item in data.pop("experts", []) or ())
        return cls(
            constraints=constraints,
            fallback_policy=fallback_policy,
            experts=experts,
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )

    def resolved_experts(self, track: TrackName) -> tuple[OCOExpertConfig, ...]:
        if self.experts:
            return self.experts
        if track == "sector":
            return (
                OCOExpertConfig("s1_quant_core", 0.40, {"track": "sector"}),
                OCOExpertConfig("risk_parity", 0.20, {"track": "sector"}),
                OCOExpertConfig("sector_rotation", 0.30, {"track": "sector"}),
                OCOExpertConfig("kg_moe_lite", 0.10, {"track": "sector"}),
            )
        return (
            OCOExpertConfig("s1_quant_core", 0.40, {"track": "macro"}),
            OCOExpertConfig("risk_parity", 0.25, {"track": "macro"}),
            OCOExpertConfig("robust_bl", 0.25, {"track": "macro"}),
            OCOExpertConfig("conservative_ensemble", 0.10, {"track": "macro"}),
        )


@dataclass(frozen=True)
class OCOEnsembleAgent:
    """Meta-allocate across valid experts and fall back deterministically on unsafe output."""

    config: OCOEnsembleConfig = field(default_factory=OCOEnsembleConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "OCOEnsembleAgent":
        return cls(OCOEnsembleConfig.from_mapping(values))

    def make_decision(
        self,
        *,
        track: TrackName | None = None,
        fund_pool: list[str] | tuple[str, ...] | None = None,
        historical_prices: dict[str, list[dict[str, Any]]] | None = None,
        news: list[dict[str, Any]] | None = None,
        current_portfolio: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_track = track or self.config.track
        pool = tuple(fund_pool or get_fund_pool(resolved_track))
        historical_prices = historical_prices or {}
        current_portfolio = current_portfolio or {}
        fallback = ConservativeEnsembleAgent.from_config(
            {
                "track": resolved_track,
                "constraints": {
                    "max_weight": self.config.constraints.max_weight,
                    "cash_reserve": self.config.constraints.cash_reserve,
                    "max_turnover": self.config.constraints.max_turnover,
                    "rebalance_threshold": self.config.constraints.rebalance_threshold,
                },
                "fallback_policy": {
                    "constraints": {
                        "max_weight": self.config.constraints.max_weight,
                        "cash_reserve": self.config.constraints.cash_reserve,
                        "max_turnover": self.config.constraints.max_turnover,
                        "rebalance_threshold": self.config.constraints.rebalance_threshold,
                    },
                    "max_allowed_turnover": self.config.fallback_policy.max_allowed_turnover,
                },
            }
        ).make_decision
        return FallbackManager(self.config.fallback_policy).run_with_fallback(
            source_agent_name="oco_ensemble",
            primary=self._primary_decision,
            fallback=fallback,
            track=resolved_track,
            fund_pool=pool,
            historical_prices=historical_prices,
            news=news,
            current_portfolio=current_portfolio,
            decision_date=_latest_date_int(historical_prices, pool),
        )

    def _primary_decision(
        self,
        *,
        track: TrackName,
        fund_pool: tuple[str, ...],
        historical_prices: dict[str, list[dict[str, Any]]],
        news: list[dict[str, Any]] | None,
        current_portfolio: dict[str, Any],
    ) -> dict[str, Any]:
        expert_configs = self.config.resolved_experts(track)
        valid_targets: dict[str, tuple[float, dict[str, float]]] = {}
        expert_validation: dict[str, dict[str, Any]] = {}

        for expert in expert_configs:
            try:
                decision = self._build_expert(expert, track).make_decision(
                    track=track,
                    fund_pool=fund_pool,
                    historical_prices=historical_prices,
                    news=news,
                    current_portfolio=current_portfolio,
                )
                validation = validate_decision(
                    decision,
                    current_portfolio=current_portfolio,
                    historical_prices=historical_prices,
                    fund_pool=fund_pool,
                    policy=self.config.fallback_policy,
                )
                metadata = decision.get("metadata", {}) or {}
                fallback_used = bool(metadata.get("fallback_used"))
                loss = _expert_loss(validation.valid, fallback_used, validation.turnover, self.config)
                gate_score = expert.prior_weight * math.exp(-self.config.learning_rate * loss)
                expert_validation[expert.name] = {
                    "valid": validation.valid,
                    "prior_weight": expert.prior_weight,
                    "loss": loss,
                    "gate_score": gate_score,
                    "triggers": list(validation.triggers),
                    "reasons": list(validation.reasons),
                    "turnover": validation.turnover,
                    "child_fallback_used": fallback_used,
                }
                if validation.valid:
                    valid_targets[expert.name] = (gate_score, decision["target_weights"])
            except Exception as exc:
                expert_validation[expert.name] = {
                    "valid": False,
                    "prior_weight": expert.prior_weight,
                    "loss": 1.0,
                    "gate_score": 0.0,
                    "triggers": ["module_exception"],
                    "reasons": [f"{type(exc).__name__}:{exc}"],
                    "turnover": None,
                    "child_fallback_used": False,
                }

        if not valid_targets:
            raise ValueError("no_valid_experts")

        score_total = sum(score for score, _ in valid_targets.values())
        gates = {name: score / score_total for name, (score, _) in valid_targets.items()}
        blended = blend_target_weights(
            {name: (gates[name], weights) for name, (_, weights) in valid_targets.items()},
            constraints=self.config.constraints,
            assets=fund_pool,
        )
        return build_weight_decision(
            agent_name="oco_ensemble",
            track=track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            current_portfolio=current_portfolio,
            constraints=self.config.constraints,
            raw_target_weights=blended,
            reasoning="OCO-style ensemble over valid experts with deterministic penalties for unsafe child decisions.",
            metadata={
                "expert_gates": gates,
                "expert_validation": expert_validation,
                "expert_count": len(expert_configs),
                "valid_expert_count": len(valid_targets),
            },
        )

    @staticmethod
    def _build_expert(expert: OCOExpertConfig, track: TrackName) -> Any:
        config = {"track": track, **expert.config}
        if expert.name == "s1_quant_core":
            return S1QuantCoreAgent.from_config(config)
        if expert.name == "risk_parity":
            return RiskParityAgent.from_config(config)
        if expert.name == "robust_bl":
            return RobustBLAgent.from_config(config)
        if expert.name == "sector_rotation":
            return SectorRotationAgent.from_config(config)
        if expert.name == "kg_moe_lite":
            return KGMoELiteAgent.from_config(config)
        if expert.name == "conservative_ensemble":
            return ConservativeEnsembleAgent.from_config(config)
        raise KeyError(f"unknown_oco_expert:{expert.name}")


def _expert_loss(valid: bool, fallback_used: bool, turnover: float, config: OCOEnsembleConfig) -> float:
    if not valid:
        return 1.0
    loss = config.turnover_penalty * min(1.0, max(0.0, turnover))
    if fallback_used:
        loss += config.fallback_penalty
    return loss


def _latest_date_int(historical_prices: dict[str, list[dict[str, Any]]], fund_pool: tuple[str, ...]) -> int | None:
    for fund_id in fund_pool:
        rows = historical_prices.get(fund_id, [])
        if rows and rows[-1].get("date_int") is not None:
            return int(rows[-1]["date_int"])
    return None


def make_oco_ensemble_decision(**kwargs: Any) -> dict[str, Any]:
    return OCOEnsembleAgent().make_decision(**kwargs)
