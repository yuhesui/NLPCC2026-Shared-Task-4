"""Robust Black-Litterman Stage 4 agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.black_litterman import black_litterman_posterior, build_bl_inputs
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.position_sizing import estimate_current_weights, target_weights_to_trades
from nlpcc.portfolio.risk_parity import covariance_to_matrix, solve_risk_parity_vector
from nlpcc.portfolio.robust_optimizer import OptimizerConfig, optimize_long_only_mean_variance
from nlpcc.portfolio.target_weights import weights_to_vector
from nlpcc.portfolio.turnover_control import apply_turnover_limit
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import Stage1Config
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.schema import Stage2Config
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class RobustBLAgentConfig:
    track: TrackName = "macro"
    stage1: Stage1Config = field(default_factory=Stage1Config)
    stage2: Stage2Config = field(default_factory=Stage2Config)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    bl_tau: float = 0.05
    bl_risk_aversion: float = 2.5
    min_view_confidence: float = 0.05
    view_return_scale: float = 1.0
    s1_blend_weight: float = 0.35

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "RobustBLAgentConfig":
        if not values:
            return cls()
        data = dict(values)
        return cls(
            stage1=Stage1Config.from_mapping(data.pop("stage1", None)),
            stage2=Stage2Config.from_mapping(data.pop("stage2", None)),
            stage3=Stage3Config.from_mapping(data.pop("stage3", None)),
            constraints=PortfolioConstraints.from_mapping(data.pop("constraints", None)),
            optimizer=OptimizerConfig.from_mapping(data.pop("optimizer", None)),
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


@dataclass(frozen=True)
class RobustBLAgent:
    config: RobustBLAgentConfig = field(default_factory=RobustBLAgentConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "RobustBLAgent":
        return cls(RobustBLAgentConfig.from_mapping(values))

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
        state = build_stage3_state(historical_prices=historical_prices, fund_pool=pool, config=self.config.stage3)
        s1_agent = S1QuantCoreAgent.from_config({"track": resolved_track})
        s1_target = s1_agent._target_weights(state, resolved_track)
        try:
            available = state.available_funds()
            if not available:
                raise ValueError("no_available_funds")

            stage1_output = run_stage1_news_pipeline(news or [], decision_date=state.decision_date, config=self.config.stage1)
            text_state = build_stage2_text_state(stage1_output, as_of_date=state.decision_date, config=self.config.stage2)
            if not text_state.bl_views:
                raise ValueError("no_valid_bl_views")

            risk_parity_anchor = solve_risk_parity_vector(
                covariance_to_matrix(state.shrinkage_covariance, available),
                constraints=self.config.constraints,
            )
            s1_vector = weights_to_vector(s1_target, available)
            anchor = (
                (1.0 - self.config.s1_blend_weight) * risk_parity_anchor
                + self.config.s1_blend_weight * s1_vector
            )
            bl_inputs = build_bl_inputs(
                covariance=state.shrinkage_covariance,
                assets=available,
                anchor_weights=anchor,
                text_state=text_state,
                risk_aversion=self.config.bl_risk_aversion,
                tau=self.config.bl_tau,
                min_confidence=self.config.min_view_confidence,
                view_return_scale=self.config.view_return_scale,
            )
            posterior = black_litterman_posterior(bl_inputs, tau=self.config.bl_tau)
            raw_target = optimize_long_only_mean_variance(
                expected_returns=posterior.posterior_returns,
                covariance_matrix=bl_inputs.covariance,
                assets=available,
                constraints=self.config.constraints,
                anchor_weights=anchor,
                config=self.config.optimizer,
                confidence=bl_inputs.view_confidence,
            )
            current_weights, _ = estimate_current_weights(current_portfolio, state.current_open_by_fund())
            target_weights = apply_turnover_limit(raw_target, current_weights, self.config.constraints)
            trades = target_weights_to_trades(
                target_weights,
                current_portfolio,
                state.current_open_by_fund(),
                rebalance_threshold=self.config.constraints.rebalance_threshold,
                cash_reserve=self.config.constraints.cash_reserve,
            )
            return {
                "trades": trades,
                "target_weights": target_weights,
                "reasoning": "Robust Black-Litterman allocation using Stage 1/2 text views, Stage 3 covariance, risk-parity/S1 anchor, and turnover control.",
                "metadata": {
                    "agent": "robust_bl",
                    "track": resolved_track,
                    "available_funds": list(available),
                    "fallback_used": False,
                    "text_view_count": len(text_state.bl_views),
                    "bl_view_count": posterior.view_count,
                    "bl_diagnostics": posterior.diagnostics,
                    "stage1_fallback_used": stage1_output.fallback_used,
                    "current_day_fields_used": ["open"],
                    "forbidden_current_fields_used": [],
                    "stage3_diagnostics": state.diagnostics,
                    "stage2_diagnostics": text_state.diagnostics,
                },
            }
        except Exception as exc:
            fallback = s1_agent.make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"robust_bl_failure:{type(exc).__name__}:{exc}"
            fallback["metadata"]["agent"] = "robust_bl_fallback_s1"
            return fallback


def make_robust_bl_decision(**kwargs: Any) -> dict[str, Any]:
    return RobustBLAgent().make_decision(**kwargs)
