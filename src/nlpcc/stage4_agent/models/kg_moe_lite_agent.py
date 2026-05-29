"""Deterministic KG-MoE-Lite Track 2 agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.position_sizing import estimate_current_weights, target_weights_to_trades
from nlpcc.portfolio.target_weights import normalize_weight_dict, project_long_only_capped_weights
from nlpcc.portfolio.turnover_control import apply_turnover_limit
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import Stage1Config
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.schema import Stage2Config
from nlpcc.stage3_trade.models.equal_weight_state import equal_weight
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from nlpcc.stage4_agent.models.sector_rotation_agent import (
    apply_news_tilt,
    sector_news_scores,
    smooth_weights_by_correlation,
)


@dataclass(frozen=True)
class KGMoELiteConfig:
    track: TrackName = "sector"
    stage1: Stage1Config = field(default_factory=Stage1Config)
    stage2: Stage2Config = field(default_factory=Stage2Config)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=lambda: PortfolioConstraints(max_weight=0.25))
    news_tilt_strength: float = 1.25
    graph_smoothing_strength: float = 0.35
    use_news: bool = True
    use_graph: bool = True

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "KGMoELiteConfig":
        if not values:
            return cls()
        data = dict(values)
        return cls(
            stage1=Stage1Config.from_mapping(data.pop("stage1", None)),
            stage2=Stage2Config.from_mapping(data.pop("stage2", None)),
            stage3=Stage3Config.from_mapping(data.pop("stage3", None)),
            constraints=PortfolioConstraints.from_mapping(data.pop("constraints", None))
            if "constraints" in data
            else PortfolioConstraints(max_weight=0.25),
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


def deterministic_expert_gates(*, text_confidence: float, correlation_edge_count: int, use_news: bool, use_graph: bool) -> dict[str, float]:
    gates = {"trend": 0.55, "equal": 0.10, "news": 0.0, "graph": 0.0}
    if use_news and text_confidence > 0:
        gates["news"] = 0.20 + min(0.10, 0.10 * text_confidence)
    if use_graph and correlation_edge_count > 0:
        gates["graph"] = 0.15
    total = sum(gates.values())
    return {name: weight / total for name, weight in gates.items() if weight > 0}


@dataclass(frozen=True)
class KGMoELiteAgent:
    config: KGMoELiteConfig = field(default_factory=KGMoELiteConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "KGMoELiteAgent":
        return cls(KGMoELiteConfig.from_mapping(values))

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
            stage1_output = run_stage1_news_pipeline(news or [], decision_date=state.decision_date, config=self.config.stage1)
            text_state = build_stage2_text_state(stage1_output, as_of_date=state.decision_date, config=self.config.stage2)
            available = state.available_funds()
            total = self.config.constraints.invested_weight
            equal = equal_weight(available, total=total)
            trend = normalize_weight_dict(state.sector_trend_weight, total=total) or equal
            news_weights = apply_news_tilt(
                trend,
                sector_news_scores(text_state, available),
                strength=self.config.news_tilt_strength,
                total=total,
            )
            graph_weights = smooth_weights_by_correlation(
                news_weights if self.config.use_news else trend,
                state.correlation_graph if self.config.use_graph else (),
                strength=self.config.graph_smoothing_strength,
                total=total,
            )
            text_confidence = (
                sum(row.confidence for row in text_state.sector_impact_panel) / len(text_state.sector_impact_panel)
                if text_state.sector_impact_panel
                else 0.0
            )
            gates = deterministic_expert_gates(
                text_confidence=text_confidence,
                correlation_edge_count=len(state.correlation_graph),
                use_news=self.config.use_news,
                use_graph=self.config.use_graph,
            )
            experts = {"equal": equal, "trend": trend, "news": news_weights, "graph": graph_weights}
            raw: dict[str, float] = {}
            for expert_name, gate in gates.items():
                for fund_id, weight in experts[expert_name].items():
                    raw[fund_id] = raw.get(fund_id, 0.0) + gate * weight
            projected = project_long_only_capped_weights(raw, available, max_weight=self.config.constraints.max_weight, total=total)
            current_weights, _ = estimate_current_weights(current_portfolio, state.current_open_by_fund())
            target_weights = apply_turnover_limit(projected, current_weights, self.config.constraints)
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
                "reasoning": "KG-MoE-Lite: deterministic mixture of equal, trend, sector-news, and correlation-graph experts.",
                "metadata": {
                    "agent": "kg_moe_lite",
                    "track": resolved_track,
                    "fallback_used": False,
                    "expert_gates": gates,
                    "sector_impact_count": len(text_state.sector_impact_panel),
                    "sector_graph_edge_count": len(text_state.sector_graph_edges),
                    "correlation_edge_count": len(state.correlation_graph),
                    "current_day_fields_used": ["open"],
                    "forbidden_current_fields_used": [],
                },
            }
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": "sector"}).make_decision(
                track="sector",
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "kg_moe_lite_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"kg_moe_lite_failure:{type(exc).__name__}:{exc}"
            return fallback


def make_kg_moe_lite_decision(**kwargs: Any) -> dict[str, Any]:
    return KGMoELiteAgent().make_decision(**kwargs)
