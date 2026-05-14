"""S1 Track 2 sector trend-following quant core allocator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.data.features import momentum_return
from nlpcc4.execution.constraints import project_long_only
from nlpcc4.execution.target_weights import validate_target_weights
from nlpcc4.execution.turnover import apply_no_trade_band, apply_turnover_cap, estimate_turnover
from nlpcc4.strategies.shared.sector_trend import sector_trend_targets
from nlpcc4.strategies.track2_sector.universe import TRACK2_UNIVERSE


@dataclass
class Track2S1QuantCore:
    """Sector trend-following with top-k, concentration cap, and turnover cap."""

    config: Mapping[str, Any]
    name: str = "s1_quant_core"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        fund_pool = tuple(context.fund_pool or TRACK2_UNIVERSE)
        signals = self.config.get("signals", {})
        portfolio = self.config.get("portfolio", {})
        execution = self.config.get("execution", {})
        top_k = int(signals.get("top_k", 5))
        window = int(signals.get("momentum_window", 20))
        raw = sector_trend_targets(
            context.historical_prices,
            fund_pool=fund_pool,
            top_k=top_k,
            momentum_window=window,
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
            max_weight=portfolio.get("max_single_weight", 0.22),
        )
        projected = project_long_only(
            raw,
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.22),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        previous = {asset: float(context.previous_weights.get(asset, 0.0)) for asset in fund_pool}
        banded = apply_no_trade_band(
            previous,
            projected,
            float(execution.get("no_trade_band", portfolio.get("no_trade_band", 0.015)) or 0.0),
            universe=fund_pool,
        )
        capped = apply_turnover_cap(
            previous,
            banded,
            execution.get("max_daily_turnover", portfolio.get("max_daily_turnover", 0.20)),
            universe=fund_pool,
        )
        final_weights = {asset: max(0.0, float(capped.get(asset, 0.0))) for asset in fund_pool}
        total = sum(final_weights.values())
        if total > 1.0:
            final_weights = {asset: weight / total for asset, weight in final_weights.items()}
        validate_target_weights(final_weights)
        scores = {asset: momentum_return(context.historical_prices.get(asset, ()), window) for asset in fund_pool}
        diagnostics = {
            "strategy": self.name,
            "top_k": top_k,
            "momentum_window": window,
            "signal_values": scores,
            "selected_assets": [asset for asset, weight in final_weights.items() if weight > 1e-6],
            "turnover": estimate_turnover(previous, final_weights),
            "concentration": sum(weight * weight for weight in final_weights.values()),
        }
        return StrategyOutput(final_weights, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track2S1QuantCore:
    """Build the Track 2 S1 strategy."""
    return Track2S1QuantCore(config or {})
