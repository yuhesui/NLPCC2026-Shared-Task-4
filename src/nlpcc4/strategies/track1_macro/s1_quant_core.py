"""S1 Track 1 robust quant core allocator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.data.features import max_drawdown, momentum_breadth, multi_horizon_momentum, zscore
from nlpcc4.execution.constraints import project_long_only
from nlpcc4.execution.target_weights import validate_target_weights
from nlpcc4.execution.turnover import apply_no_trade_band, apply_turnover_cap, estimate_turnover
from nlpcc4.strategies.shared.risk_budget import allocate_risk_budget
from nlpcc4.strategies.track1_macro.universe import TRACK1_DEFENSIVE_ASSETS, TRACK1_UNIVERSE


@dataclass
class Track1S1QuantCore:
    """Inverse-vol + multi-horizon momentum + defensive sleeve."""

    config: Mapping[str, Any]
    name: str = "s1_quant_core"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        fund_pool = tuple(context.fund_pool or TRACK1_UNIVERSE)
        signals = self.config.get("signals", {})
        portfolio = self.config.get("portfolio", {})
        risk = self.config.get("risk", {})
        execution = self.config.get("execution", {})

        windows = tuple(int(x) for x in signals.get("momentum_windows", (5, 20, 60)))
        vol_window = int(signals.get("volatility_window", 20))
        momentum_scores = multi_horizon_momentum(context.historical_prices, windows)
        momentum_z = zscore(momentum_scores)
        raw_scores = {asset: max(0.05, 1.0 + float(momentum_z.get(asset, 0.0))) for asset in fund_pool}
        signal_weights = allocate_risk_budget(
            raw_scores,
            context.historical_prices,
            volatility_window=vol_window,
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
            max_weight=portfolio.get("max_single_weight", 0.30),
            universe=fund_pool,
        )

        breadth_window = int(risk.get("breadth_window", 20))
        breadth = momentum_breadth(context.historical_prices, breadth_window)
        defensive_assets = tuple(asset for asset in TRACK1_DEFENSIVE_ASSETS if asset in fund_pool)
        defensive_weight = 0.0
        if breadth < float(risk.get("weak_breadth_threshold", 0.40)):
            defensive_weight = float(risk.get("defensive_weight_when_weak", 0.35))

        risky_drawdowns = [
            max_drawdown(context.historical_prices.get(asset, ()), int(risk.get("drawdown_window", 60)))
            for asset in fund_pool
            if asset not in defensive_assets
        ]
        worst_drawdown = min(risky_drawdowns) if risky_drawdowns else 0.0
        if worst_drawdown < -abs(float(risk.get("drawdown_trigger", 0.10))):
            defensive_weight = max(defensive_weight, float(risk.get("defensive_weight_on_drawdown", 0.45)))

        if defensive_weight > 0 and defensive_assets:
            defensive_each = defensive_weight / len(defensive_assets)
            adjusted = {asset: signal_weights.get(asset, 0.0) * (1.0 - defensive_weight) for asset in fund_pool}
            for asset in defensive_assets:
                adjusted[asset] = adjusted.get(asset, 0.0) + defensive_each
            signal_weights = adjusted

        projected = project_long_only(
            signal_weights,
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.30),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        previous = {asset: float(context.previous_weights.get(asset, 0.0)) for asset in fund_pool}
        banded = apply_no_trade_band(
            previous,
            projected,
            float(execution.get("no_trade_band", portfolio.get("no_trade_band", 0.02)) or 0.0),
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
        diagnostics = {
            "strategy": self.name,
            "breadth": breadth,
            "worst_drawdown": worst_drawdown,
            "defensive_weight": defensive_weight,
            "turnover": estimate_turnover(previous, final_weights),
            "momentum_scores": momentum_scores,
            "selected_assets": [asset for asset, weight in final_weights.items() if weight > 1e-6],
            "concentration": sum(weight * weight for weight in final_weights.values()),
        }
        return StrategyOutput(final_weights, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track1S1QuantCore:
    """Build the Track 1 S1 strategy."""
    return Track1S1QuantCore(config or {})
