"""Track 2 sector-rotation agent."""

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
from nlpcc.stage2_text_store.schema import Stage2Config, Stage2TextState
from nlpcc.stage3_trade.models.equal_weight_state import equal_weight
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config, Stage3State
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class SectorRotationConfig:
    track: TrackName = "sector"
    stage1: Stage1Config = field(default_factory=Stage1Config)
    stage2: Stage2Config = field(default_factory=Stage2Config)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=lambda: PortfolioConstraints(max_weight=0.25))
    trend_weight: float = 0.70
    news_weight: float = 0.20
    graph_weight: float = 0.10
    equal_weight: float = 0.0
    news_tilt_strength: float = 1.5
    graph_smoothing_strength: float = 0.25
    use_news: bool = True
    use_graph: bool = True
    use_trend: bool = True

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "SectorRotationConfig":
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


def sector_news_scores(text_state: Stage2TextState, fund_pool: tuple[str, ...]) -> dict[str, float]:
    pool = set(fund_pool)
    scores: dict[str, float] = {}
    for row in text_state.sector_impact_panel:
        for etf_id in row.etf_ids:
            if etf_id in pool:
                scores[etf_id] = scores.get(etf_id, 0.0) + row.signed_intensity
    return scores


def apply_news_tilt(base_weights: dict[str, float], scores: dict[str, float], *, strength: float, total: float) -> dict[str, float]:
    if not scores:
        return dict(base_weights)
    raw = {
        fund_id: weight * max(0.0, 1.0 + (strength * scores.get(fund_id, 0.0)))
        for fund_id, weight in base_weights.items()
    }
    for fund_id, score in scores.items():
        if fund_id not in raw and score > 0:
            raw[fund_id] = strength * score
    return normalize_weight_dict(raw, total=total) or dict(base_weights)


def smooth_weights_by_correlation(
    weights: dict[str, float],
    correlation_graph: tuple[dict[str, float | str], ...],
    *,
    strength: float,
    total: float,
) -> dict[str, float]:
    if not correlation_graph or strength <= 0:
        return dict(weights)
    raw = dict(weights)
    for edge in correlation_graph:
        corr = float(edge.get("correlation", 0.0))
        if corr <= 0:
            continue
        left = str(edge["left"])
        right = str(edge["right"])
        average = 0.5 * (weights.get(left, 0.0) + weights.get(right, 0.0))
        pull = strength * corr
        raw[left] = ((1.0 - pull) * raw.get(left, 0.0)) + (pull * average)
        raw[right] = ((1.0 - pull) * raw.get(right, 0.0)) + (pull * average)
    return normalize_weight_dict(raw, total=total) or dict(weights)


def blend_sector_sleeves(
    *,
    state: Stage3State,
    text_state: Stage2TextState | None,
    config: SectorRotationConfig,
) -> dict[str, float]:
    available = state.available_funds()
    total = config.constraints.invested_weight
    equal = equal_weight(available, total=total)
    trend = normalize_weight_dict(state.sector_trend_weight, total=total) or equal
    base_for_news = trend if config.use_trend else equal
    news = base_for_news
    if config.use_news and text_state is not None:
        news = apply_news_tilt(
            base_for_news,
            sector_news_scores(text_state, available),
            strength=config.news_tilt_strength,
            total=total,
        )
    graph = smooth_weights_by_correlation(
        base_for_news,
        state.correlation_graph if config.use_graph else (),
        strength=config.graph_smoothing_strength,
        total=total,
    )

    sleeves: dict[str, tuple[float, dict[str, float]]] = {}
    if config.use_trend:
        sleeves["trend"] = (config.trend_weight, trend)
    if config.use_news:
        sleeves["news"] = (config.news_weight, news)
    if config.use_graph:
        sleeves["graph"] = (config.graph_weight, graph)
    if config.equal_weight > 0 or not sleeves:
        sleeves["equal"] = (config.equal_weight if sleeves else 1.0, equal)
    raw: dict[str, float] = {}
    for sleeve_weight, weights in sleeves.values():
        for fund_id, weight in weights.items():
            raw[fund_id] = raw.get(fund_id, 0.0) + (sleeve_weight * weight)
    return project_long_only_capped_weights(raw, available, max_weight=config.constraints.max_weight, total=total)


@dataclass(frozen=True)
class SectorRotationAgent:
    config: SectorRotationConfig = field(default_factory=SectorRotationConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "SectorRotationAgent":
        return cls(SectorRotationConfig.from_mapping(values))

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
            stage1_output = None
            text_state = None
            if self.config.use_news:
                stage1_output = run_stage1_news_pipeline(news or [], decision_date=state.decision_date, config=self.config.stage1)
                text_state = build_stage2_text_state(stage1_output, as_of_date=state.decision_date, config=self.config.stage2)
            raw_target = blend_sector_sleeves(state=state, text_state=text_state, config=self.config)
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
                "reasoning": "Track 2 sector rotation: trend baseline plus optional sector-news tilt and correlation graph smoothing.",
                "metadata": {
                    "agent": "sector_rotation",
                    "track": resolved_track,
                    "available_funds": list(state.available_funds()),
                    "fallback_used": False,
                    "ablation": {
                        "use_news": self.config.use_news,
                        "use_graph": self.config.use_graph,
                        "use_trend": self.config.use_trend,
                    },
                    "sector_impact_count": len(text_state.sector_impact_panel) if text_state else 0,
                    "sector_graph_edge_count": len(text_state.sector_graph_edges) if text_state else 0,
                    "correlation_edge_count": len(state.correlation_graph),
                    "stage1_fallback_used": stage1_output.fallback_used if stage1_output else None,
                    "current_day_fields_used": ["open"],
                    "forbidden_current_fields_used": [],
                    "stage3_diagnostics": state.diagnostics,
                },
            }
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": "sector"}).make_decision(
                track="sector",
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "sector_rotation_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"sector_rotation_failure:{type(exc).__name__}:{exc}"
            return fallback


def make_sector_rotation_decision(**kwargs: Any) -> dict[str, Any]:
    return SectorRotationAgent().make_decision(**kwargs)
