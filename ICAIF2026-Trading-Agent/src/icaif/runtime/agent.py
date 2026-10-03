"""The registered trading agent: context -> (SUBMIT weights | HOLD) + trace.

No human chooses weights: the agent runs configured pipelines in a fixed
fallback order and emits either a validated target or an explicit HOLD.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

import numpy as np

from icaif.portfolio.pipeline import PipelineResult, PortfolioPipeline
from icaif.runtime.decision_trace import DecisionTrace, FallbackEvent
from icaif.runtime.fallback import FallbackPolicy, classify_exception
from icaif.runtime.safety import input_issues, output_issues
from icaif.runtime.state import AgentState, DecisionContext

BLOCKING_INPUT_ISSUES = {
    "view_as_of_mismatch",
    "decision_time_after_deadline",
    "stale_market_data",
    "missing_prices",
    "inconsistent_portfolio_state",
    "invalid_nav",
}


@dataclass
class AgentDecision:
    action: str  # SUBMIT | HOLD
    weights: np.ndarray
    pipeline: str | None
    trace: DecisionTrace
    result: PipelineResult | None = None
    alerts: list[str] = field(default_factory=list)


class TradingAgent:
    def __init__(self, name: str, pipelines: Mapping[str, PortfolioPipeline], policy: FallbackPolicy,
                 *, max_staleness: timedelta = timedelta(hours=72), hard_max_turnover: float = 2.0) -> None:
        missing = [p for p in policy.chain if p not in pipelines]
        if missing:
            raise ValueError(f"fallback chain references unknown pipelines {missing}")
        self.name = name
        self.pipelines = dict(pipelines)
        self.policy = policy
        self.max_staleness = max_staleness
        self.hard_max_turnover = hard_max_turnover

    def restore(self, state: AgentState) -> None:
        for p in self.pipelines.values():
            p.restore(state)

    def decide(self, ctx: DecisionContext, state: AgentState) -> AgentDecision:
        trace = DecisionTrace(
            phase=ctx.phase,
            round_id=ctx.round_id,
            decision_time=ctx.decision_time.isoformat(),
            deadline=ctx.deadline.isoformat(),
            execution_time=ctx.execution_time.isoformat(),
            agent=self.name,
        )
        view = ctx.market_state
        trace.information = {
            "bars_visible": view.n_bars,
            "last_bar_end": view.last_bar_end.isoformat() if view.last_bar_end else None,
            "staleness_seconds": view.staleness().total_seconds() if view.staleness() is not None else None,
            "text": ctx.text_state.summary() if ctx.text_state is not None else None,
            "macro_keys": sorted(ctx.macro_state) if ctx.macro_state else [],
            "market_source": view.panel.source,
            "synthetic_market": view.panel.synthetic,
        }
        trace.portfolio = {"previous_weights": ctx.current_weights, "nav_estimate": ctx.nav_estimate,
                           "previous_gross": float(np.sum(ctx.current_weights))}
        current = np.asarray(ctx.current_weights, dtype=float)
        alerts: list[str] = []

        issues = input_issues(ctx, max_staleness=self.max_staleness, min_bars=2)
        blocking = [i for i in issues if i in BLOCKING_INPUT_ISSUES]
        trace.information["input_issues"] = issues
        if blocking:
            trace.add_fallback(FallbackEvent("input_issue", ",".join(blocking), "inputs", "HOLD"))
            return self._hold(trace, current, alerts)

        for name in self.policy.chain:
            pipeline = self.pipelines[name]
            try:
                result = pipeline.run(ctx, state)
            except Exception as error:  # noqa: BLE001 - classified and recorded below
                kind = classify_exception(error)
                trace.errors.append(f"{name}: {kind}: {error}")
                if kind == "critical_leakage":
                    alerts.append("critical_leakage")
                    if self.policy.strict:
                        raise
                    trace.add_fallback(FallbackEvent(kind, str(error), name, "HOLD"))
                    return self._hold(trace, current, alerts)
                if kind.startswith("unexpected_exception"):
                    alerts.append(kind)
                    if self.policy.strict:
                        raise
                trace.add_fallback(FallbackEvent(kind, str(error)[:300], name, "next_in_chain"))
                continue
            if result.action == "HOLD":
                self._fill_trace(trace, result)
                trace.action = "HOLD"
                trace.constraints["hold_reason"] = result.diagnostics.get("hold_reason")
                return AgentDecision("HOLD", current, name, trace, result, alerts)
            problems = output_issues(result.target, current, cons=pipeline.cons, max_turnover=self.hard_max_turnover)
            if problems:
                trace.add_fallback(FallbackEvent("invalid_output", ",".join(problems), name, "next_in_chain"))
                continue
            self._fill_trace(trace, result)
            trace.action = "SUBMIT"
            trace.submitted_weights = {k: v for k, v in zip(_symbols(), result.target.tolist(), strict=True)}
            return AgentDecision("SUBMIT", result.target, name, trace, result, alerts)

        trace.add_fallback(FallbackEvent("chain_exhausted", "all pipelines failed", "chain", self.policy.terminal_action))
        return self._hold(trace, current, alerts)

    def commit(self, ctx: DecisionContext, state: AgentState, decision: AgentDecision) -> None:
        if decision.result is not None and decision.pipeline is not None:
            self.pipelines[decision.pipeline].commit(ctx, state, decision.result)
        else:
            state.rounds_decided += 1
            state.last_round_id = ctx.round_id
        if decision.trace.fallback_events:
            state.fallbacks_used += 1

    @staticmethod
    def _hold(trace: DecisionTrace, current: np.ndarray, alerts: list[str]) -> AgentDecision:
        trace.action = "HOLD"
        return AgentDecision("HOLD", current, None, trace, None, alerts)

    @staticmethod
    def _fill_trace(trace: DecisionTrace, result: PipelineResult) -> None:
        st, dg = result.stages, result.diagnostics
        trace.quant = {
            "strategy": dg.get("strategy"),
            "alpha": dg.get("alpha"),
            "alpha_score": st.get("alpha_score"),
            "base_unit": st.get("base_unit"),
            "base_after_exposure": st.get("base"),
            "exposure": dg.get("exposure"),
            "covariance": dg.get("covariance"),
            "erc": dg.get("erc"),
            "optimizer": dg.get("optimizer"),
        }
        trace.nlp = {"overlay": dg.get("overlay"), "overlay_delta": st.get("overlay_delta")}
        trace.portfolio.update({"unconstrained_proposal": st.get("pre_turnover"), "final_target": st.get("final")})
        trace.constraints = {"turnover_steps": dg.get("turnover_steps"), "gross": dg.get("gross")}
        trace.costs = {"expected_turnover": dg.get("expected_turnover"), "expected_fee": dg.get("expected_fee"),
                       "news_driven_turnover": dg.get("news_driven_turnover")}


def _symbols() -> tuple[str, ...]:
    from icaif.core.universe import SYMBOLS

    return SYMBOLS


def build_agent(config: Mapping[str, Any]) -> TradingAgent:
    """Agent from a system config: ``{"name", "pipelines": {name: cfg}, "fallback_chain": [...], "strict": bool}``."""

    pipelines = {name: PortfolioPipeline({"name": name, **cfg}) for name, cfg in config["pipelines"].items()}
    policy = FallbackPolicy(chain=tuple(config["fallback_chain"]), strict=bool(config.get("strict", False)))
    hours = float(config.get("max_staleness_hours", 72.0))
    return TradingAgent(config["name"], pipelines, policy, max_staleness=timedelta(hours=hours),
                        hard_max_turnover=float(config.get("hard_max_turnover", 2.0)))
