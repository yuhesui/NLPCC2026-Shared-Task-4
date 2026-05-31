"""ARMOR-OMD exponentiated-weight ensemble MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from pathlib import Path
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.stage3_trade.models.base_allocator_performance import build_base_allocator_performance_state
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage4_agent.ensemble_utils import blend_target_weights, build_weight_decision
from nlpcc.stage4_agent.models.kg_moe_lite_agent import KGMoELiteAgent
from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent
from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from nlpcc.stage4_agent.models.sector_rotation_agent import SectorRotationAgent


@dataclass
class ARMOROMDConfig:
    track: TrackName = "macro"
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    learning_rate: float = 4.0
    turnover_penalty: float = 0.15
    state_path: str | None = None
    experts: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "ARMOROMDConfig":
        if not values:
            return cls()
        data = dict(values)
        if "experts" in data:
            data["experts"] = tuple(str(item) for item in data["experts"])
        return cls(
            constraints=PortfolioConstraints.from_mapping(data.pop("constraints", None)),
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


@dataclass
class ARMOROMDAgent:
    config: ARMOROMDConfig = field(default_factory=ARMOROMDConfig)
    log_weights: dict[str, float] = field(default_factory=dict)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "ARMOROMDAgent":
        agent = cls(ARMOROMDConfig.from_mapping(values))
        agent._load_state()
        return agent

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
        try:
            state = build_stage3_state(historical_prices=historical_prices, fund_pool=pool)
            targets: dict[str, dict[str, float]] = {}
            for name in self._experts(resolved_track):
                decision = self._build_expert(name, resolved_track).make_decision(
                    track=resolved_track,
                    fund_pool=pool,
                    historical_prices=historical_prices,
                    news=news,
                    current_portfolio=current_portfolio,
                )
                targets[name] = dict(decision.get("target_weights", {}) or {})
            performance = build_base_allocator_performance_state(state, targets)
            gates = self._update_gates(performance.get("scores", {}), targets)
            blended = blend_target_weights(
                {name: (gates[name], targets[name]) for name in gates},
                constraints=self.config.constraints,
                assets=pool,
            )
            self._save_state()
            return build_weight_decision(
                agent_name="armor_omd",
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
                constraints=self.config.constraints,
                raw_target_weights=blended,
                reasoning="ARMOR-OMD MVP: exponentiated-weight blend over base allocators with prior-return performance proxies.",
                metadata={
                    "expert_gates": gates,
                    "performance_state": performance,
                    "state_persisted": bool(self.config.state_path),
                    "method_maturity": "functional_mvp",
                },
            )
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": resolved_track}).make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "armor_omd_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"armor_omd_failure:{type(exc).__name__}:{exc}"
            return fallback

    def _experts(self, track: TrackName) -> tuple[str, ...]:
        if self.config.experts:
            return self.config.experts
        if track == "sector":
            return ("s1_quant_core", "risk_parity", "sector_rotation", "kg_moe_lite")
        return ("s1_quant_core", "risk_parity", "robust_bl")

    def _update_gates(self, scores: dict[str, float], targets: dict[str, dict[str, float]]) -> dict[str, float]:
        for name in targets:
            self.log_weights.setdefault(name, 0.0)
            self.log_weights[name] += self.config.learning_rate * float(scores.get(name, 0.0))
            self.log_weights[name] -= self.config.turnover_penalty * sum(abs(weight) for weight in targets[name].values())
        max_log = max(self.log_weights.values()) if self.log_weights else 0.0
        raw = {name: math.exp(value - max_log) for name, value in self.log_weights.items() if name in targets}
        total = sum(raw.values()) or 1.0
        return {name: round(value / total, 8) for name, value in raw.items()}

    def _build_expert(self, name: str, track: TrackName) -> Any:
        if name == "s1_quant_core":
            return S1QuantCoreAgent.from_config({"track": track})
        if name == "risk_parity":
            return RiskParityAgent.from_config({"track": track})
        if name == "robust_bl":
            return RobustBLAgent.from_config({"track": track})
        if name == "sector_rotation":
            return SectorRotationAgent.from_config({"track": track})
        if name == "kg_moe_lite":
            return KGMoELiteAgent.from_config({"track": track})
        raise KeyError(f"unknown_armor_expert:{name}")

    def _load_state(self) -> None:
        if not self.config.state_path:
            return
        path = Path(self.config.state_path)
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.log_weights.update({str(key): float(value) for key, value in payload.get("log_weights", {}).items()})

    def _save_state(self) -> None:
        if not self.config.state_path:
            return
        path = Path(self.config.state_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"log_weights": self.log_weights}, indent=2, sort_keys=True), encoding="utf-8")


def make_armor_omd_decision(**kwargs: Any) -> dict[str, Any]:
    return ARMOROMDAgent().make_decision(**kwargs)
