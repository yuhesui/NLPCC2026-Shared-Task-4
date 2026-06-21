"""S1 no-news quantitative fallback agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.stage3_trade.models.cash_feasibility import plan_rebalance_trades
from nlpcc.stage3_trade.models.drawdown import drawdown_penalty
from nlpcc.stage3_trade.models.equal_weight_state import cap_and_redistribute, normalize_weights
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config, Stage3State


@dataclass(frozen=True)
class S1QuantCoreConfig:
    track: TrackName = "macro"
    stage3: Stage3Config = field(default_factory=Stage3Config)
    inverse_vol_weight: float = 0.55
    momentum_weight: float = 0.30
    sector_trend_weight: float = 0.15
    drawdown_penalty_weight: float = 0.35
    cash_reserve: float = 0.03
    max_weight: float = 0.35
    rebalance_threshold: float = 0.01

    @classmethod
    def for_track(cls, track: TrackName) -> "S1QuantCoreConfig":
        if track == "sector":
            return cls(track=track, inverse_vol_weight=0.35, momentum_weight=0.15, sector_trend_weight=0.50)
        return cls(track=track)

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "S1QuantCoreConfig":
        if not values:
            return cls()
        data = dict(values)
        stage3 = Stage3Config.from_mapping(data.pop("stage3", None))
        track = data.get("track", "macro")
        base = cls.for_track(track)
        merged = {field_name: getattr(base, field_name) for field_name in cls.__dataclass_fields__}
        merged.update({key: value for key, value in data.items() if key in cls.__dataclass_fields__})
        merged["stage3"] = stage3
        return cls(**merged)


@dataclass(frozen=True)
class S1QuantCoreAgent:
    """No-news S1 benchmark: inverse-volatility plus trend/risk filters."""

    config: S1QuantCoreConfig = field(default_factory=S1QuantCoreConfig)

    @classmethod
    def for_track(cls, track: TrackName) -> "S1QuantCoreAgent":
        return cls(S1QuantCoreConfig.for_track(track))

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "S1QuantCoreAgent":
        return cls(S1QuantCoreConfig.from_mapping(values))

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
        state = build_stage3_state(
            historical_prices=historical_prices,
            fund_pool=pool,
            config=self.config.stage3,
        )
        target_weights = self._target_weights(state, resolved_track)
        trades = plan_rebalance_trades(
            target_weights,
            current_portfolio,
            state.current_open_by_fund(),
            rebalance_threshold=self.config.rebalance_threshold,
            cash_reserve=self.config.cash_reserve,
        )
        return {
            "trades": trades,
            "target_weights": target_weights,
            "reasoning": "S1 no-news quant core: inverse-volatility, momentum/trend, drawdown and breadth filters.",
            "metadata": {
                "agent": "s1_quant_core",
                "track": resolved_track,
                "available_funds": list(state.available_funds()),
                "current_day_fields_used": ["open"],
                "forbidden_current_fields_used": [],
                "stage3_diagnostics": state.diagnostics,
            },
        }

    def _target_weights(self, state: Stage3State, track: TrackName) -> dict[str, float]:
        if track == "sector":
            raw = self._blend_weights(
                {
                    "inverse_volatility": (self.config.inverse_vol_weight, state.inverse_volatility_weight),
                    "momentum": (self.config.momentum_weight, state.momentum_weight),
                    "sector_trend": (self.config.sector_trend_weight, state.sector_trend_weight),
                }
            )
        else:
            raw = self._blend_weights(
                {
                    "inverse_volatility": (self.config.inverse_vol_weight, state.inverse_volatility_weight),
                    "momentum": (self.config.momentum_weight, state.momentum_weight),
                    "equal_weight": (self.config.sector_trend_weight, state.equal_weight),
                }
            )

        adjusted: dict[str, float] = {}
        for fund_id, weight in raw.items():
            asset = state.assets.get(fund_id)
            penalty = drawdown_penalty(asset.drawdown if asset else 0.0)
            breadth_boost = asset.breadth if asset else 0.5
            adjusted[fund_id] = weight * max(0.0, 1.0 - (self.config.drawdown_penalty_weight * penalty)) * (
                0.75 + (0.5 * breadth_boost)
            )
        invested_total = max(0.0, 1.0 - self.config.cash_reserve)
        normalized = normalize_weights(adjusted, total=invested_total)
        fallback = normalize_weights(state.equal_weight, total=invested_total)
        return cap_and_redistribute(normalized or fallback, self.config.max_weight, total=invested_total)

    @staticmethod
    def _blend_weights(named_weights: dict[str, tuple[float, dict[str, float]]]) -> dict[str, float]:
        raw: dict[str, float] = {}
        for blend_weight, weights in named_weights.values():
            for fund_id, weight in weights.items():
                raw[fund_id] = raw.get(fund_id, 0.0) + (blend_weight * weight)
        return raw


def make_s1_decision(**kwargs: Any) -> dict[str, Any]:
    return S1QuantCoreAgent().make_decision(**kwargs)
