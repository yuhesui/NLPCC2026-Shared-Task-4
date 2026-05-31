"""HGF-MPC one-step constrained controller MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.target_weights import project_long_only_capped_weights
from nlpcc.stage3_trade.models.kalman_drift import build_kalman_drift_state
from nlpcc.stage3_trade.models.price_hmm_state import build_price_hmm_state
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.ensemble_utils import build_weight_decision
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class HGFMPCAgentConfig:
    track: TrackName = "macro"
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    drift_weight: float = 0.70
    risk_weight: float = 0.30
    risk_off_scale: float = 0.70

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "HGFMPCAgentConfig":
        if not values:
            return cls()
        data = dict(values)
        return cls(
            stage3=Stage3Config.from_mapping(data.pop("stage3", None)),
            constraints=PortfolioConstraints.from_mapping(data.pop("constraints", None)),
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


@dataclass(frozen=True)
class HGFMPCAgent:
    config: HGFMPCAgentConfig = field(default_factory=HGFMPCAgentConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "HGFMPCAgent":
        return cls(HGFMPCAgentConfig.from_mapping(values))

    def make_decision(
        self,
        *,
        track: TrackName | None = None,
        fund_pool: list[str] | tuple[str, ...] | None = None,
        historical_prices: dict[str, list[dict[str, Any]]] | None = None,
        news: list[dict[str, Any]] | None = None,
        current_portfolio: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del news
        resolved_track = track or self.config.track
        pool = tuple(fund_pool or get_fund_pool(resolved_track))
        historical_prices = historical_prices or {}
        current_portfolio = current_portfolio or {}
        try:
            state = build_stage3_state(historical_prices=historical_prices, fund_pool=pool, config=self.config.stage3)
            kalman = build_kalman_drift_state(state)
            hmm = build_price_hmm_state(state)
            risk_scale = self.config.risk_off_scale if hmm.get("dominant_regime") == "risk_off" else 1.0
            raw: dict[str, float] = {}
            for fund_id in state.available_funds():
                drift = float(kalman["assets"][fund_id]["drift"])
                confidence = float(kalman["assets"][fund_id]["confidence"])
                volatility = max(state.assets[fund_id].volatility, 1e-6)
                score = max(0.0, self.config.drift_weight * drift * confidence + self.config.risk_weight / volatility)
                raw[fund_id] = score * risk_scale
            if not any(raw.values()):
                raw = state.inverse_volatility_weight
            projected = project_long_only_capped_weights(
                raw,
                state.available_funds(),
                max_weight=self.config.constraints.max_weight,
                total=self.config.constraints.invested_weight * risk_scale,
            )
            return build_weight_decision(
                agent_name="hgf_mpc",
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
                constraints=self.config.constraints,
                raw_target_weights=projected,
                reasoning="HGF-MPC MVP: one-step constrained allocation from Kalman-smoothed drift and price-regime state.",
                metadata={
                    "kalman_state": kalman,
                    "hmm_state": hmm,
                    "risk_scale": risk_scale,
                    "method_maturity": "functional_mvp_one_step",
                },
            )
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": resolved_track}).make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "hgf_mpc_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"hgf_mpc_failure:{type(exc).__name__}:{exc}"
            return fallback


def make_hgf_mpc_decision(**kwargs: Any) -> dict[str, Any]:
    return HGFMPCAgent().make_decision(**kwargs)
