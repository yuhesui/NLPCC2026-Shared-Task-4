"""Runtime fallback validation and deterministic recovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from nlpcc.core.fund_universe import TrackName
from nlpcc.portfolio.constraints import PortfolioConstraints, validate_weight_constraints
from nlpcc.portfolio.position_sizing import estimate_current_weights
from nlpcc.portfolio.turnover_control import portfolio_turnover
from nlpcc.runtime.decision_trace import DecisionTrace, FallbackEvent, attach_decision_trace
from nlpcc.runtime.dependency_guard import missing_required_dependencies


DecisionFactory = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class FallbackPolicy:
    constraints: PortfolioConstraints = field(default_factory=PortfolioConstraints)
    max_allowed_turnover: float = 0.35
    required_dependencies: tuple[str, ...] = ()
    fallback_agent_name: str = "s1_quant_core"

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "FallbackPolicy":
        if not values:
            return cls()
        data = dict(values)
        constraints = PortfolioConstraints.from_mapping(data.pop("constraints", None))
        if "required_dependencies" in data:
            data["required_dependencies"] = tuple(data["required_dependencies"])
        return cls(
            constraints=constraints,
            **{key: value for key, value in data.items() if key in cls.__dataclass_fields__},
        )


@dataclass(frozen=True)
class DecisionValidationResult:
    valid: bool
    triggers: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    turnover: float = 0.0


def _current_open_by_fund(historical_prices: dict[str, list[dict[str, Any]]], fund_pool: tuple[str, ...]) -> dict[str, float]:
    prices: dict[str, float] = {}
    for fund_id in fund_pool:
        rows = historical_prices.get(fund_id, [])
        if not rows:
            continue
        value = rows[-1].get("open")
        if value not in (None, ""):
            prices[fund_id] = float(value)
    return prices


def validate_decision(
    decision: dict[str, Any],
    *,
    current_portfolio: dict[str, Any],
    historical_prices: dict[str, list[dict[str, Any]]],
    fund_pool: tuple[str, ...],
    policy: FallbackPolicy,
) -> DecisionValidationResult:
    triggers: list[str] = []
    reasons: list[str] = []
    weights = decision.get("target_weights")
    if not isinstance(weights, dict) or not weights:
        triggers.append("invalid_weights")
        reasons.append("missing_target_weights")
        weights = {}
    else:
        constraint_issues = validate_weight_constraints(weights, policy.constraints)
        if constraint_issues:
            triggers.append("invalid_weights")
            reasons.extend(constraint_issues)
    metadata = decision.get("metadata", {}) or {}
    if metadata.get("forbidden_current_fields_used"):
        triggers.append("price_leakage")
        reasons.append("forbidden_current_fields_used")
    if metadata.get("dependency_failures"):
        triggers.append("missing_dependency")
        reasons.append("dependency_failures")
    if metadata.get("fallback_used") and metadata.get("fallback_reason"):
        triggers.append("child_fallback")
        reasons.append(str(metadata["fallback_reason"]))
    current_weights, _ = estimate_current_weights(current_portfolio, _current_open_by_fund(historical_prices, fund_pool))
    turnover = portfolio_turnover(current_weights, weights if isinstance(weights, dict) else {})
    if turnover > policy.max_allowed_turnover + 1e-8:
        triggers.append("high_turnover")
        reasons.append(f"turnover={turnover:.6f}>limit={policy.max_allowed_turnover:.6f}")
    return DecisionValidationResult(
        valid=not triggers,
        triggers=tuple(dict.fromkeys(triggers)),
        reasons=tuple(reasons),
        turnover=turnover,
    )


@dataclass(frozen=True)
class FallbackManager:
    policy: FallbackPolicy = field(default_factory=FallbackPolicy)

    def dependency_failures(self) -> tuple[str, ...]:
        return missing_required_dependencies(self.policy.required_dependencies)

    def run_with_fallback(
        self,
        *,
        source_agent_name: str,
        primary: DecisionFactory,
        fallback: DecisionFactory,
        track: TrackName,
        fund_pool: tuple[str, ...],
        historical_prices: dict[str, list[dict[str, Any]]],
        news: list[dict[str, Any]] | None,
        current_portfolio: dict[str, Any],
        decision_date: int | None = None,
    ) -> dict[str, Any]:
        trace = DecisionTrace(agent=source_agent_name, track=track, decision_date=decision_date)
        dependency_failures = self.dependency_failures()
        if dependency_failures:
            return self._fallback_decision(
                fallback=fallback,
                track=track,
                fund_pool=fund_pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
                trace=trace.add_event(
                    FallbackEvent(
                        trigger="missing_dependency",
                        reason="missing_required_dependencies:" + ",".join(dependency_failures),
                        source_agent=source_agent_name,
                        fallback_agent=self.policy.fallback_agent_name,
                    )
                ),
            )
        try:
            decision = primary(
                track=track,
                fund_pool=fund_pool,
                historical_prices=historical_prices,
                news=news,
                current_portfolio=current_portfolio,
            )
        except Exception as exc:
            return self._fallback_decision(
                fallback=fallback,
                track=track,
                fund_pool=fund_pool,
                historical_prices=historical_prices,
                current_portfolio=current_portfolio,
                trace=trace.add_event(
                    FallbackEvent(
                        trigger="module_exception",
                        reason=f"{type(exc).__name__}:{exc}",
                        source_agent=source_agent_name,
                        fallback_agent=self.policy.fallback_agent_name,
                    )
                ),
            )

        validation = validate_decision(
            decision,
            current_portfolio=current_portfolio,
            historical_prices=historical_prices,
            fund_pool=fund_pool,
            policy=self.policy,
        )
        if validation.valid:
            diagnostics = dict(trace.diagnostics)
            diagnostics["turnover"] = validation.turnover
            trace = DecisionTrace(
                agent=trace.agent,
                track=trace.track,
                decision_date=trace.decision_date,
                created_at_utc=trace.created_at_utc,
                fallback_events=trace.fallback_events,
                diagnostics=diagnostics,
            )
            return attach_decision_trace(decision, trace)

        reason_by_trigger = dict(zip(validation.triggers, validation.reasons or validation.triggers))
        for trigger in validation.triggers:
            trace = trace.add_event(
                FallbackEvent(
                    trigger=trigger,
                    reason=reason_by_trigger.get(trigger, trigger),
                    source_agent=source_agent_name,
                    fallback_agent=self.policy.fallback_agent_name,
                )
            )
        return self._fallback_decision(
            fallback=fallback,
            track=track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            current_portfolio=current_portfolio,
            trace=trace,
        )

    def _fallback_decision(
        self,
        *,
        fallback: DecisionFactory,
        track: TrackName,
        fund_pool: tuple[str, ...],
        historical_prices: dict[str, list[dict[str, Any]]],
        current_portfolio: dict[str, Any],
        trace: DecisionTrace,
    ) -> dict[str, Any]:
        decision = fallback(
            track=track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            news=None,
            current_portfolio=current_portfolio,
        )
        metadata = dict(decision.get("metadata", {}) or {})
        metadata["fallback_used"] = True
        decision = dict(decision)
        decision["metadata"] = metadata
        return attach_decision_trace(decision, trace)
