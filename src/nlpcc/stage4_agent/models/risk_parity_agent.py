"""Risk-parity Stage 4 agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.portfolio.constraints import PortfolioConstraints
from nlpcc.portfolio.position_sizing import estimate_current_weights, target_weights_to_trades
from nlpcc.portfolio.risk_parity import solve_risk_parity_weights
from nlpcc.portfolio.turnover_control import apply_turnover_limit
from nlpcc.stage3_trade.pipeline import build_stage3_state
from nlpcc.stage3_trade.schema import Stage3Config
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent


@dataclass(frozen=True)
class RiskParityAgentConfig:
    track: TrackName = "macro"
    stage3: Stage3Config = field(default_factory=Stage3Config)
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "RiskParityAgentConfig":
        if not values:
            return cls()
        data = dict(values)
        stage3 = Stage3Config.from_mapping(data.pop("stage3", None))
        constraints = PortfolioConstraints.from_mapping(data.pop("constraints", None))
        return cls(
            stage3=stage3,
            constraints=constraints,
            **{key: value for key, value in data.items() if key in {"track"}},
        )


@dataclass(frozen=True)
class RiskParityAgent:
    config: RiskParityAgentConfig = field(default_factory=RiskParityAgentConfig)

    @classmethod
    def from_config(cls, values: dict[str, Any] | None) -> "RiskParityAgent":
        return cls(RiskParityAgentConfig.from_mapping(values))

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
        state = build_stage3_state(historical_prices=historical_prices, fund_pool=pool, config=self.config.stage3)
        try:
            available = state.available_funds()
            raw_target = solve_risk_parity_weights(
                state.shrinkage_covariance,
                available,
                constraints=self.config.constraints,
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
                "reasoning": "Risk parity allocation with long-only caps and turnover control.",
                "metadata": {
                    "agent": "risk_parity",
                    "track": resolved_track,
                    "available_funds": list(available),
                    "fallback_used": False,
                    "current_day_fields_used": ["open"],
                    "forbidden_current_fields_used": [],
                    "stage3_diagnostics": state.diagnostics,
                },
            }
        except Exception as exc:
            fallback = S1QuantCoreAgent.from_config({"track": resolved_track}).make_decision(
                track=resolved_track,
                fund_pool=pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
            )
            fallback["metadata"]["fallback_used"] = True
            fallback["metadata"]["fallback_reason"] = f"risk_parity_failure:{type(exc).__name__}"
            fallback["metadata"]["agent"] = "risk_parity_fallback_s1"
            return fallback


def make_risk_parity_decision(**kwargs: Any) -> dict[str, Any]:
    return RiskParityAgent().make_decision(**kwargs)
