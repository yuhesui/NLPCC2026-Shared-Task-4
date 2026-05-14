"""Strategy registry for scripts and tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.data.news_features import keyword_exposure_scores, news_sentiment_score
from nlpcc4.execution.constraints import project_long_only
from nlpcc4.strategies.shared.equal_weight import equal_weight_targets
from nlpcc4.strategies.shared.inverse_vol import inverse_vol_targets
from nlpcc4.strategies.shared.momentum import momentum_targets
from nlpcc4.strategies.shared.persistence import persistence_targets
from nlpcc4.strategies.shared.random_constrained import random_constrained_targets
from nlpcc4.strategies.shared.sector_trend import sector_trend_targets
from nlpcc4.strategies.track1_macro.rule_based_macro import rule_based_macro_targets
from nlpcc4.strategies.track1_macro.s1_quant_core import Track1S1QuantCore
from nlpcc4.strategies.track1_macro.s2_llm_regime import Track1S2LLMRegime
from nlpcc4.strategies.track1_macro.s3_llm_alpha_tilt import Track1S3LLMAlphaTilt
from nlpcc4.strategies.track1_macro.s4_event_exposure import Track1S4EventExposure
from nlpcc4.strategies.track1_macro.universe import TRACK1_UNIVERSE
from nlpcc4.strategies.track2_sector.s1_quant_core import Track2S1QuantCore
from nlpcc4.strategies.track2_sector.s2_llm_regime import Track2S2LLMRegime
from nlpcc4.strategies.track2_sector.s3_llm_alpha_tilt import Track2S3LLMAlphaTilt
from nlpcc4.strategies.track2_sector.s4_event_exposure import Track2S4EventExposure
from nlpcc4.strategies.track2_sector.universe import TRACK2_UNIVERSE


@dataclass
class BaselineStrategy:
    """Adapter that exposes S0 baseline functions as strategy objects."""

    baseline_name: str
    config: Mapping[str, Any]
    name: str = "s0_baseline"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        portfolio = self.config.get("portfolio", {})
        signals = self.config.get("signals", {})
        fund_pool = tuple(context.fund_pool)
        max_weight = portfolio.get("max_single_weight", 0.30 if context.track == "track1" else 0.22)
        cash_buffer = float(portfolio.get("cash_buffer", 0.01))
        if self.baseline_name == "s0_equal_weight":
            weights = equal_weight_targets(fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
            signal_values = {}
        elif self.baseline_name == "s0_inverse_vol":
            weights = inverse_vol_targets(
                context.historical_prices,
                volatility_window=int(signals.get("volatility_window", 20)),
                cash_buffer=cash_buffer,
                max_weight=max_weight,
                universe=fund_pool,
            )
            signal_values = {"volatility_window": signals.get("volatility_window", 20)}
        elif self.baseline_name == "s0_momentum":
            weights = momentum_targets(
                context.historical_prices,
                windows=tuple(signals.get("momentum_windows", (20,))),
                cash_buffer=cash_buffer,
                max_weight=max_weight,
                universe=fund_pool,
            )
            signal_values = {"momentum_windows": signals.get("momentum_windows", (20,))}
        elif self.baseline_name == "s0_sector_trend":
            weights = sector_trend_targets(
                context.historical_prices,
                fund_pool=fund_pool,
                top_k=int(signals.get("top_k", 5)),
                momentum_window=int(signals.get("momentum_window", 20)),
                cash_buffer=cash_buffer,
                max_weight=max_weight,
            )
            signal_values = {"top_k": signals.get("top_k", 5)}
        elif self.baseline_name == "s0_persistence":
            weights = persistence_targets(context.previous_weights, fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
            signal_values = {"previous_weight_sum": sum(context.previous_weights.values())}
        elif self.baseline_name == "s0_rule_based_macro":
            if context.track == "track1":
                weights = rule_based_macro_targets(context.historical_prices, context.news, fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
            else:
                weights = sector_trend_targets(context.historical_prices, fund_pool=fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
            signal_values = {"news_sentiment": news_sentiment_score(context.news)}
        elif self.baseline_name == "s0_news_sentiment":
            sentiment = news_sentiment_score(context.news)
            raw = {asset: 1.0 + max(0.0, sentiment) for asset in fund_pool}
            if sentiment < -0.2:
                raw = {asset: 0.5 for asset in fund_pool}
                if context.track == "track1":
                    for asset in ("000012.SH", "518880.SH"):
                        if asset in raw:
                            raw[asset] = 3.0
            keyword_scores = keyword_exposure_scores(context.news, {asset: (asset.split(".")[0],) for asset in fund_pool})
            raw = {asset: raw.get(asset, 1.0) + keyword_scores.get(asset, 0.0) for asset in fund_pool}
            weights = project_long_only(raw, universe=fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
            signal_values = {"news_sentiment": sentiment}
        elif self.baseline_name == "s0_random_constrained":
            weights = random_constrained_targets(
                fund_pool,
                seed=int(signals.get("random_seed", 7)),
                decision_date=context.decision_date,
                cash_buffer=cash_buffer,
                max_weight=max_weight,
            )
            signal_values = {"random_seed": signals.get("random_seed", 7)}
        else:
            raise ValueError(f"unknown S0 baseline: {self.baseline_name}")
        diagnostics = {
            "strategy": self.baseline_name,
            "signal_values": signal_values,
            "selected_assets": [asset for asset, weight in weights.items() if weight > 1e-6],
            "concentration": sum(weight * weight for weight in weights.values()),
        }
        return StrategyOutput(weights, diagnostics)


def _track_specific(track: str, track1_cls: Callable, track2_cls: Callable, config: Mapping[str, Any]):
    return track1_cls(config) if track == "track1" else track2_cls(config)


def get_default_universe(track: str) -> tuple[str, ...]:
    """Return official public universe by track."""
    if track == "track1":
        return TRACK1_UNIVERSE
    if track == "track2":
        return TRACK2_UNIVERSE
    raise ValueError("track must be track1 or track2")


def build_strategy(track: str, strategy_name: str, config: Mapping[str, Any]):
    """Build a strategy object by name."""
    if strategy_name.startswith("s0_"):
        return BaselineStrategy(strategy_name, config)
    if strategy_name == "s1_quant_core":
        return _track_specific(track, Track1S1QuantCore, Track2S1QuantCore, config)
    if strategy_name == "s2_llm_regime":
        return _track_specific(track, Track1S2LLMRegime, Track2S2LLMRegime, config)
    if strategy_name == "s3_llm_alpha_tilt":
        return _track_specific(track, Track1S3LLMAlphaTilt, Track2S3LLMAlphaTilt, config)
    if strategy_name == "s4_event_exposure":
        return _track_specific(track, Track1S4EventExposure, Track2S4EventExposure, config)
    raise ValueError(f"Unknown strategy: {strategy_name}")


def list_strategies() -> tuple[str, ...]:
    return (
        "s0_equal_weight",
        "s0_inverse_vol",
        "s0_momentum",
        "s0_sector_trend",
        "s0_persistence",
        "s0_rule_based_macro",
        "s0_news_sentiment",
        "s0_random_constrained",
        "s1_quant_core",
        "s2_llm_regime",
        "s3_llm_alpha_tilt",
        "s4_event_exposure",
    )


def list_registered_strategies() -> list[str]:
    """Backward-compatible list function."""
    return list(list_strategies())
