"""Conservative deterministic ensemble with S1/risk-parity fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.runtime.fallback_manager import FallbackManager, FallbackPolicy, validate_decision
from nlpcc.stage4_agent.ensemble_utils import blend_target_weights, build_weight_decision
from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class ConservativeEnsembleConfig:
    track: TrackName = "macro"
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    fallback_policy: FallbackPolicy = field(default_factory=lambda: FallbackPolicy(max_allowed_turnover=0.60))
    s1_weight: float = 0.65
    risk_parity_weight: float = 0.35
    s1_config: dict[str, Any] = field(default_factory=dict)
    risk_parity_config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "ConservativeEnsembleConfig":
        if not values:
            return cls()
        data = dict(values)
        constraints = PortfolioConstraints.from_mapping(data.pop("constraints", None))
        fallback_policy = FallbackPolicy.from_mapping(data.pop("fallback_policy", None))
        if "fallback_policy" not in values:
            fallback_policy = FallbackPolicy(constraints=constraints, max_allowed_turnover=0.60)
        return cls(
            constraints=constraints,
            fallback_policy=fallback_policy,
            s1_config=dict(data.pop("s1_config", {}) or {}),
            risk_parity_config=dict(data.pop("risk_parity_config", {}) or {}),
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


@dataclass(frozen=True)
class ConservativeEnsembleAgent:
    """Blend S1 and risk parity, then delegate safety failures to S1."""

    config: ConservativeEnsembleConfig = field(default_factory=ConservativeEnsembleConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "ConservativeEnsembleAgent":
        return cls(ConservativeEnsembleConfig.from_mapping(values))

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
        fallback = S1QuantCoreAgent.from_config({"track": resolved_track, **self.config.s1_config}).make_decision
        manager = FallbackManager(self.config.fallback_policy)

        return manager.run_with_fallback(
            source_agent_name="conservative_ensemble",
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
        del news
        children = {
            "s1_quant_core": (
                self.config.s1_weight,
                S1QuantCoreAgent.from_config({"track": track, **self.config.s1_config}),
            ),
            "risk_parity": (
                self.config.risk_parity_weight,
                RiskParityAgent.from_config(
                    {
                        "track": track,
                        "constraints": {
                            "max_weight": self.config.constraints.max_weight,
                            "cash_reserve": self.config.constraints.cash_reserve,
                            "max_turnover": self.config.constraints.max_turnover,
                            "rebalance_threshold": self.config.constraints.rebalance_threshold,
                        },
                        **self.config.risk_parity_config,
                    }
                ),
            ),
        }
        valid_targets: dict[str, tuple[float, dict[str, float]]] = {}
        child_validation: dict[str, dict[str, Any]] = {}
        child_fallback_reasons: list[str] = []

        for child_name, (prior_weight, child_agent) in children.items():
            try:
                decision = child_agent.make_decision(
                    track=track,
                    fund_pool=fund_pool,
                    historical_prices=historical_prices,
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
                child_validation[child_name] = {
                    "valid": validation.valid,
                    "triggers": list(validation.triggers),
                    "reasons": list(validation.reasons),
                    "turnover": validation.turnover,
                    "child_fallback_used": bool(metadata.get("fallback_used")),
                }
                if validation.valid:
                    valid_targets[child_name] = (prior_weight, decision["target_weights"])
                elif validation.reasons:
                    child_fallback_reasons.extend(f"{child_name}:{reason}" for reason in validation.reasons)
            except Exception as exc:
                child_validation[child_name] = {
                    "valid": False,
                    "triggers": ["module_exception"],
                    "reasons": [f"{type(exc).__name__}:{exc}"],
                    "turnover": None,
                    "child_fallback_used": False,
                }
                child_fallback_reasons.append(f"{child_name}:{type(exc).__name__}:{exc}")

        if not valid_targets:
            raise ValueError("no_valid_child_decisions")

        total_gate = sum(weight for weight, _ in valid_targets.values())
        gates = {name: weight / total_gate for name, (weight, _) in valid_targets.items()}
        blended = blend_target_weights(
            {name: (gates[name], weights) for name, (_, weights) in valid_targets.items()},
            constraints=self.config.constraints,
            assets=fund_pool,
        )
        return build_weight_decision(
            agent_name="conservative_ensemble",
            track=track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            current_portfolio=current_portfolio,
            constraints=self.config.constraints,
            raw_target_weights=blended,
            reasoning="Conservative ensemble blending valid S1 and risk-parity sleeves with deterministic fallback.",
            metadata={
                "child_agents": list(children),
                "valid_child_agents": list(valid_targets),
                "ensemble_gates": gates,
                "child_validation": child_validation,
                "child_fallback_reasons": child_fallback_reasons,
            },
        )


def _latest_date_int(historical_prices: dict[str, list[dict[str, Any]]], fund_pool: tuple[str, ...]) -> int | None:
    for fund_id in fund_pool:
        rows = historical_prices.get(fund_id, [])
        if rows and rows[-1].get("date_int") is not None:
            return int(rows[-1]["date_int"])
    return None


def make_conservative_ensemble_decision(**kwargs: Any) -> dict[str, Any]:
    return ConservativeEnsembleAgent().make_decision(**kwargs)
