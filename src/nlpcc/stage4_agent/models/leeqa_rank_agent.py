"""LEEQA-Rank deterministic Track 2 ranking MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.target_weights import project_long_only_capped_weights
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import Stage1Config
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.schema import Stage2Config
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.ensemble_utils import build_weight_decision
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class LEEQARankConfig:
    track: TrackName = "sector"
    stage1: Stage1Config = field(default_factory=Stage1Config)
    stage2: Stage2Config = field(default_factory=Stage2Config)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=lambda: PortfolioConstraints(max_weight=0.25))
    top_k: int = 6
    momentum_weight: float = 0.45
    inverse_vol_weight: float = 0.25
    sentiment_weight: float = 0.15
    graph_weight: float = 0.10
    analogue_weight: float = 0.05
    temperature: float = 0.35

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "LEEQARankConfig":
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


@dataclass(frozen=True)
class LEEQARankAgent:
    config: LEEQARankConfig = field(default_factory=LEEQARankConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "LEEQARankAgent":
        return cls(LEEQARankConfig.from_mapping(values))

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
            state = build_stage3_state(historical_prices=historical_prices, fund_pool=pool, config=self.config.stage3)
            stage1 = run_stage1_news_pipeline(news or [], decision_date=state.decision_date, config=self.config.stage1)
            text_state = build_stage2_text_state(stage1, as_of_date=state.decision_date, config=self.config.stage2)
            text_rows = {str(row.get("asset")): row for row in text_state.rank_feature_panel}
            scores: dict[str, float] = {}
            for fund_id in state.available_funds():
                asset = state.assets[fund_id]
                row = text_rows.get(fund_id, {})
                inv_vol = 1.0 / max(asset.volatility, 1e-6)
                scores[fund_id] = (
                    self.config.momentum_weight * asset.momentum
                    + self.config.inverse_vol_weight * min(2.0, inv_vol / 100.0)
                    + self.config.sentiment_weight * float(row.get("sector_score", 0.0) or 0.0)
                    + self.config.graph_weight * float(row.get("graph_score", 0.0) or 0.0)
                    + self.config.analogue_weight * float(row.get("analogue_score", 0.0) or 0.0)
                )
            raw = _topk_softmax(scores, top_k=self.config.top_k, temperature=self.config.temperature)
            projected = project_long_only_capped_weights(
                raw,
                state.available_funds(),
                max_weight=self.config.constraints.max_weight,
                total=self.config.constraints.invested_weight,
            )
            return build_weight_decision(
                agent_name="leeqa_rank",
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
                constraints=self.config.constraints,
                raw_target_weights=projected,
                reasoning="LEEQA-Rank MVP: deterministic cross-sectional rank score from price, text, graph, and analogue features.",
                metadata={
                    "top_k": self.config.top_k,
                    "rank_scores": {key: round(value, 8) for key, value in scores.items()},
                    "stage1_fallback_used": stage1.fallback_used,
                    "rank_feature_count": len(text_state.rank_feature_panel),
                },
            )
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": "sector"}).make_decision(
                track="sector",
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "leeqa_rank_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"leeqa_rank_failure:{type(exc).__name__}:{exc}"
            return fallback


def _topk_softmax(scores: dict[str, float], *, top_k: int, temperature: float) -> dict[str, float]:
    selected = sorted(scores.items(), key=lambda item: item[1], reverse=True)[: max(1, top_k)]
    if not selected:
        return {}
    max_score = selected[0][1]
    raw = {asset: math.exp((score - max_score) / max(temperature, 1e-6)) for asset, score in selected}
    total = sum(raw.values()) or 1.0
    return {asset: value / total for asset, value in raw.items()}


def make_leeqa_rank_decision(**kwargs: Any) -> dict[str, Any]:
    return LEEQARankAgent().make_decision(**kwargs)
