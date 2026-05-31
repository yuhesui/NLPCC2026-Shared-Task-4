"""CEVA-KF / CIGA stable causal-overlay MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.target_weights import project_long_only_capped_weights
from nlpcc.stage1_news.models.entity_sector_mapper import map_sectors_to_track2_etfs
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import Stage1Config
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.schema import Stage2Config
from nlpcc.stage3_trade.models.kalman_drift import build_kalman_drift_state
from nlpcc.stage3_trade.models.stable_effect_estimator import estimate_stable_effects
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.ensemble_utils import build_weight_decision
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class CEVAKFCIGAConfig:
    track: TrackName = "macro"
    stage1: Stage1Config = field(default_factory=Stage1Config)
    stage2: Stage2Config = field(default_factory=Stage2Config)
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    overlay_strength: float = 0.20
    kalman_strength: float = 0.10

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "CEVAKFCIGAConfig":
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
class CEVAKFCIGAAgent:
    config: CEVAKFCIGAConfig = field(default_factory=CEVAKFCIGAConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "CEVAKFCIGAAgent":
        return cls(CEVAKFCIGAConfig.from_mapping(values))

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
            s1 = S1QuantCoreAgent.from_config({"track": resolved_track}).make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            state = build_stage3_state(historical_prices=historical_prices, fund_pool=pool, config=self.config.stage3)
            stage1 = run_stage1_news_pipeline(news or [], decision_date=state.decision_date, config=self.config.stage1)
            text_state = build_stage2_text_state(stage1, as_of_date=state.decision_date, config=self.config.stage2)
            kalman = build_kalman_drift_state(state)
            stable = estimate_stable_effects(
                (row.sector, row.signed_intensity * row.confidence) for row in text_state.sector_impact_panel
            )
            tilts = _asset_tilts(pool, text_state.causal_event_graph.get("stable_impact_by_sector", {}), stable)
            raw = dict(s1.get("target_weights", {}) or {})
            for fund_id in pool:
                drift = float(kalman.get("assets", {}).get(fund_id, {}).get("drift", 0.0))
                raw[fund_id] = max(
                    0.0,
                    raw.get(fund_id, 0.0)
                    * (1.0 + self.config.overlay_strength * tilts.get(fund_id, 0.0))
                    + self.config.kalman_strength * max(0.0, drift),
                )
            projected = project_long_only_capped_weights(
                raw,
                pool,
                max_weight=self.config.constraints.max_weight,
                total=self.config.constraints.invested_weight,
            )
            return build_weight_decision(
                agent_name="ceva_kf_ciga",
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
                constraints=self.config.constraints,
                raw_target_weights=projected,
                reasoning="CEVA-KF/CIGA MVP: stable event-impact graph plus Kalman-filtered conservative overlay on S1.",
                metadata={
                    "stage1_fallback_used": stage1.fallback_used,
                    "causal_event_graph": text_state.causal_event_graph,
                    "stable_effects": stable,
                    "kalman_state": kalman,
                    "asset_tilts": tilts,
                    "method_maturity": "functional_mvp_stable_effect_graph",
                },
            )
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": resolved_track}).make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["agent"] = "ceva_kf_ciga_fallback_s1"
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"ceva_kf_ciga_failure:{type(exc).__name__}:{exc}"
            return fallback


def _asset_tilts(pool: tuple[str, ...], sector_scores: dict[str, float], stable: dict[str, Any]) -> dict[str, float]:
    tilts: dict[str, float] = {}
    for sector, score in sector_scores.items():
        for asset in map_sectors_to_track2_etfs((sector,)):
            if asset in pool:
                tilts[asset] = tilts.get(asset, 0.0) + float(score)
    if not tilts and pool:
        aggregate = sum(float(item.get("mean_effect", 0.0)) * float(item.get("stability", 0.0)) for item in stable.get("effects", {}).values())
        for asset in pool:
            tilts[asset] = aggregate / len(pool)
    return {key: round(value, 8) for key, value in tilts.items()}


def make_ceva_kf_ciga_decision(**kwargs: Any) -> dict[str, Any]:
    return CEVAKFCIGAAgent().make_decision(**kwargs)
