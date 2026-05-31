"""Belief-State Adaptive Risk-Parity MVP agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.position_sizing import estimate_current_weights, target_weights_to_trades
from nlpcc.portfolio.risk_parity import covariance_to_matrix, solve_risk_parity_vector
from nlpcc.portfolio.target_weights import vector_to_weights
from nlpcc.portfolio.turnover_control import apply_turnover_limit
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import Stage1Config
from nlpcc.stage2_text_store.models.belief_state import build_belief_state
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.schema import Stage2Config
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class BSARPConfig:
    track: TrackName = "macro"
    stage1: Stage1Config = field(default_factory=Stage1Config)
    stage2: Stage2Config = field(default_factory=Stage2Config)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    belief_tilt_strength: float = 0.35
    drawdown_guard: float = 0.60

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "BSARPConfig":
        if not values:
            return cls()
        data = dict(values)
        return cls(
            stage1=Stage1Config.from_mapping(data.pop("stage1", None)),
            stage2=Stage2Config.from_mapping(data.pop("stage2", None)),
            stage3=Stage3Config.from_mapping(data.pop("stage3", None)),
            constraints=PortfolioConstraints.from_mapping(data.pop("constraints", None)),
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


@dataclass(frozen=True)
class BSARPAgent:
    config: BSARPConfig = field(default_factory=BSARPConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "BSARPAgent":
        return cls(BSARPConfig.from_mapping(values))

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
        try:
            stage1 = run_stage1_news_pipeline(news or [], decision_date=state.decision_date, config=self.config.stage1)
            text_state = build_stage2_text_state(stage1, as_of_date=state.decision_date, config=self.config.stage2)
            belief = build_belief_state(text_state.flat_features, text_state.bl_views, text_state.decayed_memory)
            available = state.available_funds()
            budgets = _belief_conditioned_budgets(available, state.assets, belief, self.config)
            weights = solve_risk_parity_vector(
                covariance_to_matrix(state.shrinkage_covariance, available),
                constraints=self.config.constraints,
                budgets=budgets,
            )
            raw_target = vector_to_weights(weights, available)
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
                "reasoning": "BSA-RP MVP: belief-state conditioned risk budgets with drawdown and turnover guards.",
                "metadata": {
                    "agent": "bsa_rp",
                    "track": resolved_track,
                    "fallback_used": False,
                    "belief_state": belief,
                    "stage1_fallback_used": stage1.fallback_used,
                    "current_day_fields_used": ["open"],
                    "forbidden_current_fields_used": [],
                    "stage3_diagnostics": state.diagnostics,
                    "stage2_diagnostics": text_state.diagnostics,
                },
            }
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": resolved_track}).make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "bsa_rp_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"bsa_rp_failure:{type(exc).__name__}:{exc}"
            return fallback


def _belief_conditioned_budgets(
    assets: tuple[str, ...],
    asset_state: dict[str, Any],
    belief: dict[str, float | int],
    config: BSARPConfig,
) -> np.ndarray:
    signal = float(belief.get("weighted_expected_return_bps", 0.0)) / 100.0
    memory = float(belief.get("memory_signal_sum", 0.0))
    risk_on = max(-1.0, min(1.0, signal + 0.25 * memory))
    budgets: list[float] = []
    for fund_id in assets:
        asset = asset_state[fund_id]
        low_vol = 1.0 / max(asset.volatility, 1e-6)
        trend = max(-0.5, min(0.5, asset.momentum * 20.0))
        drawdown_penalty = 1.0 - config.drawdown_guard * min(1.0, asset.drawdown)
        budget = low_vol * (1.0 + config.belief_tilt_strength * risk_on * trend) * max(0.1, drawdown_penalty)
        budgets.append(max(1e-6, budget))
    arr = np.asarray(budgets, dtype=float)
    return arr / float(arr.sum())


def make_bsa_rp_decision(**kwargs: Any) -> dict[str, Any]:
    return BSARPAgent().make_decision(**kwargs)
