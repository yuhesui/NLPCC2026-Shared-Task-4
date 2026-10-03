"""Round-by-round backtester reproducing ICAIF decision-period accounting.

For each non-cancelled round k (chronological):
  1. freeze AS_OF = deadline - decision_lead (point-in-time views only);
  2. the agent decides SUBMIT(weights) or HOLD;
  3. execution at the round's execution time, priced at the open of the bar
     starting then (proxy for the official hourly-open execution price);
  4. B_k = NAV at execution prices before trading; E_k = NAV at the next
     included round's execution prices (or the final official close).
Valuation points = initial NAV, every E_k, every 16:00 daily close
(deduplicated by timestamp), exactly as docs/evaluation.md specifies.

Transaction costs cannot be disabled in serious runs: ``fee_rate`` must equal
0.001 unless ``research_fee_override`` is set *and* the run is marked
non-serious; the registry refuses to record overridden runs as evidence.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from icaif.backtest.execution import execute_target
from icaif.backtest.metrics import concentration_hhi, summarize_rounds
from icaif.competition.evaluation import OfficialMetrics, Period, compute_official_metrics
from icaif.competition.portfolio_state import PortfolioState
from icaif.competition.schedule import Schedule
from icaif.core.constants import FEE_RATE, INITIAL_NAV
from icaif.core.time import et_datetime
from icaif.data.market.panel import MarketPanel
from icaif.runtime.agent import TradingAgent
from icaif.runtime.state import AgentState, DecisionContext, TextState

TextProvider = Callable[[datetime], TextState]


class CostsDisabledError(ValueError):
    pass


@dataclass(frozen=True)
class BacktestConfig:
    initial_nav: float = INITIAL_NAV
    fee_rate: float = FEE_RATE
    decision_lead_minutes: float = 5.0
    serious: bool = True
    research_fee_override: bool = False
    trace_dir: Path | None = None

    def __post_init__(self) -> None:
        if self.fee_rate != FEE_RATE and (self.serious or not self.research_fee_override):
            raise CostsDisabledError(
                "fee_rate must be 0.001 (ICAIF). Non-default fees need serious=False and research_fee_override=True"
            )


@dataclass
class BacktestResult:
    metrics: OfficialMetrics
    summary: dict[str, float]
    rounds: list[dict[str, Any]]
    periods: list[Period]
    valuation_points: list[tuple[datetime, float]]
    final_state: PortfolioState
    synthetic_data: bool
    config: BacktestConfig
    alerts: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"metrics": self.metrics.as_dict(), "summary": self.summary, "synthetic_data": self.synthetic_data,
                "fee_rate": self.config.fee_rate, "serious": self.config.serious, "alerts": self.alerts}


def run_backtest(panel: MarketPanel, agent: TradingAgent, schedule: Schedule, phase: str, *,
                 config: BacktestConfig | None = None, text_provider: TextProvider | None = None,
                 macro_provider: Callable[[datetime], dict[str, Any]] | None = None) -> BacktestResult:
    cfg = config or BacktestConfig()
    rounds = schedule.phase_rounds(phase)
    if not rounds:
        raise ValueError(f"no rounds for phase {phase}")
    state = PortfolioState.initial(cfg.initial_nav)
    agent_state = AgentState(nav_peak=cfg.initial_nav)
    agent.restore(agent_state)
    periods: list[Period] = []
    points: dict[datetime, float] = {}
    rows: list[dict[str, Any]] = []
    alerts: list[str] = []
    previous: dict[str, Any] | None = None
    days = sorted({r.day for r in rounds})
    closes = {d: et_datetime(d, "16:00") for d in days}

    first_exec = rounds[0].execution_time
    points[first_exec] = cfg.initial_nav
    for k, row in enumerate(rounds):
        as_of = row.deadline - timedelta(minutes=cfg.decision_lead_minutes)
        view = panel.as_of(as_of)
        last_px = view.last_close()
        nav_est = state.nav(np.where(np.isfinite(last_px), last_px, 0.0))
        current = state.weights(np.where(np.isfinite(last_px), last_px, 0.0))
        ctx = DecisionContext(
            phase=phase, round_id=row.id, round_number=row.number, decision_time=as_of, deadline=row.deadline,
            execution_time=row.execution_time, market_state=view, portfolio_state=state, current_weights=current,
            nav_estimate=nav_est, text_state=text_provider(as_of) if text_provider else None,
            macro_state=macro_provider(as_of) if macro_provider else None, previous_decision=previous,
        )
        decision = agent.decide(ctx, agent_state)
        alerts.extend(decision.alerts)
        exec_px = panel.execution_prices(row.execution_time)
        nav_before = state.nav(exec_px)
        if decision.action == "SUBMIT":
            fill = execute_target(state, decision.weights, exec_px, fee_rate=cfg.fee_rate)
            state, notional, fee, scale = fill.state, fill.traded_notional, fill.fee, fill.funding_scale
        else:
            notional, fee, scale = 0.0, 0.0, 1.0
        agent.commit(ctx, agent_state, decision)
        # endpoint: next round's execution, or the phase's final close
        if k + 1 < len(rounds):
            end_time = rounds[k + 1].execution_time
            end_px = panel.execution_prices(end_time)
        else:
            end_time = closes[row.day]
            end_px = panel.close_at(end_time)
        nav_end = state.nav(end_px)
        periods.append(Period(nav_before, nav_end, notional))
        points[end_time] = nav_end
        for close_time in closes.values():
            if row.execution_time < close_time <= end_time and close_time not in points:
                points[close_time] = state.nav(panel.close_at(close_time))
        w_after = state.weights(exec_px)
        news_to = float(decision.result.diagnostics.get("news_driven_turnover", 0.0)) if decision.result else 0.0
        rows.append({
            "round_id": row.id, "day": row.day.isoformat(), "number": row.number, "action": decision.action,
            "pipeline": decision.pipeline, "fallback": bool(decision.trace.fallback_events),
            "nav_before": nav_before, "nav_after_period": nav_end, "traded_notional": notional, "fee": fee,
            "round_turnover": notional / nav_before if nav_before > 0 else 0.0, "funding_scale": scale,
            "gross_after": float(w_after.sum()), "names": int(np.sum(w_after > 1e-6)), "hhi": concentration_hhi(w_after),
            "news_driven_turnover": news_to,
        })
        if cfg.trace_dir is not None:
            decision.trace.costs["realised_fee"] = fee
            decision.trace.costs["realised_notional"] = notional
            decision.trace.write(cfg.trace_dir)
        previous = {"round_id": row.id, "action": decision.action, "weights": decision.weights.tolist()}
    ordered = [v for _, v in sorted(points.items())]
    metrics = compute_official_metrics(periods, ordered, initial_nav=cfg.initial_nav)
    return BacktestResult(metrics, summarize_rounds(rows), rows, periods, sorted(points.items()), state,
                          panel.synthetic, cfg, sorted(set(alerts)))
