from __future__ import annotations

import json
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import numpy as np
import pytest

from icaif.competition.portfolio_state import PortfolioState
from icaif.competition.schedule import generate_standard_schedule
from icaif.core.leakage_guard import LeakageViolation
from icaif.core.universe import SYMBOLS
from icaif.portfolio.pipeline import PortfolioPipeline
from icaif.runtime.agent import TradingAgent, build_agent
from icaif.runtime.context import PanelContextBuilder
from icaif.runtime.decision_trace import redact
from icaif.runtime.fallback import FallbackPolicy
from icaif.runtime.scheduler import LiveRunner, LocalPaperSession, RunnerConfig
from icaif.runtime.state import AgentState

SYSTEM = {"name": "t", "fallback_chain": ["primary", "fb"], "strict": False,
          "pipelines": {"primary": {"base": {"method": "erc"}, "turnover": {}},
                        "fb": {"base": {"method": "equal"}, "turnover": {}}}}


def ctx_for(world, row, *, portfolio=None, as_of=None):
    builder = PanelContextBuilder(lambda: world.panel)
    return builder.build(row, as_of or row.deadline - timedelta(minutes=5), portfolio or PortfolioState.initial(), "validation")


class Boom(PortfolioPipeline):
    def __init__(self, error):
        super().__init__({"base": {"method": "equal"}})
        self.error = error

    def run(self, ctx, state):
        raise self.error


def agent_with(primary, strict=False):
    return TradingAgent("t", {"primary": primary, "fb": PortfolioPipeline({"name": "fb", "base": {"method": "equal"}})},
                        FallbackPolicy(("primary", "fb"), strict=strict))


def test_model_failure_falls_back_with_trace(world, eval_schedule):
    row = eval_schedule.rounds[0]
    d = agent_with(Boom(np.linalg.LinAlgError("singular"))).decide(ctx_for(world, row), AgentState())
    assert d.action == "SUBMIT" and d.pipeline == "fb"
    ev = d.trace.fallback_events[0]
    assert ev.trigger.startswith("anticipated:LinAlgError") and ev.source == "primary"


def test_unexpected_error_raises_in_strict_mode_and_is_flagged_otherwise(world, eval_schedule):
    row = eval_schedule.rounds[0]
    with pytest.raises(KeyError):
        agent_with(Boom(KeyError("bug")), strict=True).decide(ctx_for(world, row), AgentState())
    d = agent_with(Boom(KeyError("bug"))).decide(ctx_for(world, row), AgentState())
    assert d.pipeline == "fb" and any(a.startswith("unexpected_exception") for a in d.alerts)


def test_leakage_is_critical_and_holds(world, eval_schedule):
    row = eval_schedule.rounds[0]
    d = agent_with(Boom(LeakageViolation("future bar"))).decide(ctx_for(world, row), AgentState())
    assert d.action == "HOLD" and "critical_leakage" in d.alerts
    with pytest.raises(LeakageViolation):
        agent_with(Boom(LeakageViolation("x")), strict=True).decide(ctx_for(world, row), AgentState())


def test_all_pipelines_fail_means_hold_not_invented_weights(world, eval_schedule):
    row = eval_schedule.rounds[0]
    agent = TradingAgent("t", {"a": Boom(np.linalg.LinAlgError()), "b": Boom(FloatingPointError())},
                         FallbackPolicy(("a", "b")))
    d = agent.decide(ctx_for(world, row), AgentState())
    assert d.action == "HOLD" and d.trace.fallback_events[-1].trigger == "chain_exhausted"
    assert np.array_equal(d.weights, np.zeros(30))  # current (all cash) holdings are kept


def test_stale_data_holds(world, eval_schedule):
    row = eval_schedule.rounds[0]
    stale_ctx = ctx_for(world, row)
    stale_ctx = replace(stale_ctx, market_state=world.panel.as_of(row.deadline - timedelta(days=10)))
    d = build_agent(SYSTEM).decide(stale_ctx, AgentState())
    assert d.action == "HOLD" and "view_as_of_mismatch" in d.trace.information["input_issues"]
    agent = TradingAgent("t", build_agent(SYSTEM).pipelines, FallbackPolicy(("primary", "fb")),
                         max_staleness=timedelta(minutes=1))
    d2 = agent.decide(ctx_for(world, row, as_of=row.deadline - timedelta(minutes=5)), AgentState())
    assert d2.action == "HOLD" and "stale_market_data" in d2.trace.information["input_issues"]


def test_inconsistent_portfolio_holds(world, eval_schedule):
    row = eval_schedule.rounds[0]
    ctx = replace(ctx_for(world, row), current_weights=np.full(30, 0.05))  # sums to 1.5
    assert build_agent(SYSTEM).decide(ctx, AgentState()).action == "HOLD"


def test_insufficient_history_uses_fallback(world):
    early = generate_standard_schedule("validation", world.panel.trading_days()[1:2]).rounds[0]
    system = json.loads(json.dumps(SYSTEM))
    system["pipelines"]["primary"]["min_history_hours"] = 200
    system["pipelines"]["fb"]["min_history_hours"] = 6.5
    d = build_agent(system).decide(ctx_for(world, early), AgentState())
    assert d.pipeline == "fb" and "InsufficientHistory" in d.trace.fallback_events[0].trigger
    system["pipelines"]["fb"]["min_history_hours"] = 200
    assert build_agent(system).decide(ctx_for(world, early), AgentState()).action == "HOLD"


def test_traces_contain_no_secrets(tmp_path, world, eval_schedule):
    row = eval_schedule.rounds[0]
    d = build_agent(SYSTEM).decide(ctx_for(world, row), AgentState())
    d.trace.information["team_token"] = "s3cr3t-token-value"
    d.trace.errors.append("auth failed for s3cr3t-token-value")
    path = d.trace.write(tmp_path, secrets=("s3cr3t-token-value",))
    text = path.read_text()
    assert "s3cr3t-token-value" not in text and "[REDACTED]" in text
    assert redact({"Authorization": "Bearer abc"}) == {"Authorization": "[REDACTED]"}
    body = json.loads(text)
    for key in ("information", "quant", "nlp", "portfolio", "constraints", "costs", "action", "submitted_weights"):
        assert key in body


# --- live runner -------------------------------------------------------------------------------

def _runner(tmp_path: Path, world, schedule, clock, *, portfolio_payload=None, mode="paper"):
    payload = {"symbols": list(SYMBOLS), "universe_confirmed": True, "rounds": [r.as_dict() for r in schedule.rounds]}
    session = LocalPaperSession(payload, lambda: clock["t"])
    if portfolio_payload is not None:
        session.portfolio = lambda phase="validation": portfolio_payload  # type: ignore[method-assign]
    cfg = RunnerConfig("validation", mode, tmp_path / "state.json", tmp_path / "ledger.jsonl", tmp_path / "traces",
                       tmp_path / "private", safety_margin_seconds=60)
    return LiveRunner(session, build_agent(SYSTEM), PanelContextBuilder(lambda: world.panel), cfg,
                      credentials=lambda: ("team", "tok-secret-123")), session


def test_runner_submits_once_and_survives_restart(tmp_path, world, eval_schedule):
    row = eval_schedule.rounds[0]
    clock = {"t": row.deadline - timedelta(minutes=10)}
    runner, session = _runner(tmp_path, world, eval_schedule, clock)
    assert runner.step()["status"] == "PAPER"
    assert runner.step()["status"] == "ALREADY_DECIDED"
    restarted, _ = _runner(tmp_path, world, eval_schedule, clock)
    restarted.session = session
    assert restarted.step()["status"] == "ALREADY_DECIDED"
    assert len(session.uploads) == 1
    assert AgentState.load(tmp_path / "state.json").rounds_decided == 1
    trace = next((tmp_path / "traces").rglob("*.trace.json")).read_text()
    assert "tok-secret-123" not in trace


def test_runner_holds_on_incomplete_portfolio(tmp_path, world, eval_schedule):
    row = eval_schedule.rounds[0]
    clock = {"t": row.deadline - timedelta(minutes=10)}
    runner, session = _runner(tmp_path, world, eval_schedule, clock, portfolio_payload={"positions": {}})
    assert runner.step()["status"] == "HELD_PORTFOLIO_UNKNOWN" and not session.uploads


def test_runner_deadline_and_external_slot(tmp_path, world, eval_schedule):
    row = eval_schedule.rounds[0]
    clock = {"t": row.deadline - timedelta(seconds=30)}
    runner, session = _runner(tmp_path, world, eval_schedule, clock)
    assert runner.step()["status"] == "SKIPPED_DEADLINE" and not session.uploads
    row2 = eval_schedule.rounds[1]
    clock["t"] = row2.deadline - timedelta(minutes=10)
    session.uploads.append({"round_id": row2.id, "selection_status": "SELECTED"})  # e.g. a manual upload
    assert runner.step()["status"] == "SLOT_CONSUMED" and len(session.uploads) == 1


def test_runner_waits_outside_windows_and_dry_run_never_uploads(tmp_path, world, eval_schedule):
    row = eval_schedule.rounds[0]
    clock = {"t": row.opens_at - timedelta(minutes=5)}
    runner, session = _runner(tmp_path, world, eval_schedule, clock, mode="dry_run")
    assert runner.step()["status"] == "WAITING"
    clock["t"] = row.deadline - timedelta(minutes=10)
    assert runner.step()["status"] == "DRY_RUN" and not session.uploads


def test_paper_mode_refuses_real_sessions(tmp_path, world, eval_schedule):
    class RealLooking:
        def schedule(self):
            return {}

    cfg = RunnerConfig("validation", "paper", tmp_path / "s", tmp_path / "l", tmp_path / "t", tmp_path / "p")
    with pytest.raises(ValueError):
        LiveRunner(RealLooking(), build_agent(SYSTEM), PanelContextBuilder(lambda: world.panel), cfg,
                   credentials=lambda: ("a", "b"))


def test_agent_state_checkpoint_roundtrip(tmp_path):
    st = AgentState(nav_peak=1.2e6, held=[True] * 30, budget_day="2026-10-08", budget_used=0.4, rounds_decided=3)
    st.save(tmp_path / "s.json")
    back = AgentState.load(tmp_path / "s.json")
    assert back.budget_used == 0.4 and back.rounds_decided == 3 and back.nav_drawdown(1.08e6) == pytest.approx(0.1)
    assert AgentState.load(tmp_path / "missing.json").rounds_decided == 0
