"""Persistent round loop for Validation/Official (dry-run, paper and live modes).

    poll schedule -> active round? -> already decided (ledger)? -> slot free (server)?
    -> read own portfolio -> freeze AS_OF -> build context (PIT data up to AS_OF)
    -> agent.decide -> trace -> HOLD (no upload) | validate twice -> claim ledger
    -> write private decision.json -> upload ONCE (live only) -> commit state

The session object is the organizer's ``kit.original_client.OriginalSession``
(live) or :class:`LocalPaperSession` (rehearsal). We only call its public
methods: ``schedule()``, ``portfolio(phase)``, ``round(round_id)``,
``decision(path)``; upload/auth/recovery logic stays in the official client.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from icaif.competition.official_adapter import kit_available, load_official_kit
from icaif.competition.portfolio_state import (
    PortfolioState,
    PortfolioStateIncomplete,
    parse_portfolio_payload,
)
from icaif.competition.schedule import DeadlineError, Round, Schedule
from icaif.competition.submission import (
    DuplicateSubmissionError,
    SubmissionLedger,
    SubmissionValidationError,
    prepare_round_submission,
    write_private_file,
)
from icaif.core.time import parse_timestamp, utc_now
from icaif.core.universe import SYMBOLS
from icaif.runtime.agent import TradingAgent
from icaif.runtime.state import AgentState, DecisionContext


class Session(Protocol):
    def schedule(self) -> dict[str, Any]: ...
    def portfolio(self, phase: str = ...) -> dict[str, Any]: ...
    def round(self, round_id: str) -> dict[str, Any]: ...
    def decision(self, path: str | Path) -> dict[str, Any]: ...


class ContextBuilder(Protocol):
    def build(self, row: Round, as_of: datetime, portfolio: PortfolioState, phase: str) -> DecisionContext: ...


def round_occupied(own_round: dict[str, Any]) -> bool:
    """Same rule as the official client: any attributable in-window attempt consumes the slot."""

    return any(item.get("selection_status") != "NOT_ELIGIBLE" for item in own_round.get("decisions", []))


@dataclass
class RunnerConfig:
    phase: str
    mode: str  # dry_run | paper | live
    state_path: Path
    ledger_path: Path
    trace_dir: Path
    private_dir: Path
    safety_margin_seconds: float = 120.0
    poll_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.mode not in ("dry_run", "paper", "live"):
            raise ValueError("mode must be dry_run, paper or live")
        if self.phase not in ("validation", "official"):
            raise ValueError("phase must be validation or official")


@dataclass
class LiveRunner:
    session: Session
    agent: TradingAgent
    builder: ContextBuilder
    config: RunnerConfig
    credentials: Callable[[], tuple[str, str]]
    log: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.config.mode == "paper" and not isinstance(self.session, LocalPaperSession):
            raise ValueError("paper mode requires LocalPaperSession; it must never upload to the organizer service")
        self.state = AgentState.load(self.config.state_path)
        self.agent.restore(self.state)
        self.ledger = SubmissionLedger(self.config.ledger_path)

    def _now(self, payload: dict[str, Any]) -> datetime:
        return parse_timestamp(payload["current_time"]) if payload.get("current_time") else utc_now()

    def step(self) -> dict[str, Any]:
        cfg = self.config
        payload = self.session.schedule()
        schedule = Schedule.from_official(payload, source="organizer")
        now = self._now(payload)
        row = schedule.active_round(now, cfg.phase)
        if row is None:
            nxt = schedule.next_round(now, cfg.phase)
            return self._record({"status": "WAITING", "next_round": nxt.id if nxt else None, "now": now.isoformat()})
        if self.ledger.get(cfg.phase, row.id) is not None:
            return self._record({"status": "ALREADY_DECIDED", "round_id": row.id})
        if now + timedelta(seconds=cfg.safety_margin_seconds) >= row.deadline:
            self.ledger.record_skip(cfg.phase, row.id, "too_close_to_deadline")
            return self._record({"status": "SKIPPED_DEADLINE", "round_id": row.id})
        if round_occupied(self.session.round(row.id)):
            self.ledger.record_skip(cfg.phase, row.id, "slot_already_consumed")
            return self._record({"status": "SLOT_CONSUMED", "round_id": row.id})
        try:
            portfolio = parse_portfolio_payload(self.session.portfolio(cfg.phase))
        except PortfolioStateIncomplete as error:
            self.ledger.record_skip(cfg.phase, row.id, f"portfolio_incomplete:{error}")
            return self._record({"status": "HELD_PORTFOLIO_UNKNOWN", "round_id": row.id, "error": str(error)})

        as_of = now  # frozen AS_OF: nothing published later may enter this decision
        ctx = self.builder.build(row, as_of, portfolio, cfg.phase)
        decision = self.agent.decide(ctx, self.state)
        team_id, team_token = self.credentials()
        trace_path = decision.trace.write(cfg.trace_dir / cfg.phase, secrets=(team_token,))
        if decision.action == "HOLD":
            self.ledger.record_skip(cfg.phase, row.id, "agent_hold")
            self._commit(ctx, decision)
            return self._record({"status": "HELD", "round_id": row.id, "trace": str(trace_path)})
        weights = dict(zip(SYMBOLS, (float(x) for x in decision.weights), strict=True))
        try:
            _, text = prepare_round_submission(row=row, weights=weights, team_id=team_id, team_token=team_token,
                                               now=utc_now() if cfg.mode == "live" else now, ledger=self.ledger,
                                               safety_margin_seconds=cfg.safety_margin_seconds)
        except (DeadlineError, SubmissionValidationError, DuplicateSubmissionError) as error:
            return self._record({"status": "NOT_SUBMITTED", "round_id": row.id, "error": f"{type(error).__name__}: {error}"})
        path = write_private_file(cfg.private_dir / cfg.phase / row.id / "decision.json", text)
        if kit_available():
            try:
                schedule_file = cfg.private_dir / cfg.phase / "schedule.json"
                schedule_file.write_text(json.dumps(payload), encoding="utf-8")
                load_official_kit().validate_decision_file(path, schedule_path=schedule_file)
            except Exception as error:  # noqa: BLE001 - official validator error types are kit-internal
                self.ledger.mark(cfg.phase, row.id, "failed_before_upload", f"official_validator:{type(error).__name__}")
                return self._record({"status": "OFFICIAL_VALIDATION_FAILED", "round_id": row.id})
        if cfg.mode == "live":
            receipt = self.session.decision(path)
            self.ledger.mark(cfg.phase, row.id, "submitted", str(receipt.get("status", "")))
        elif cfg.mode == "paper":
            receipt = self.session.decision(path)  # LocalPaperSession only (checked at construction)
            self.ledger.mark(cfg.phase, row.id, "paper")
        else:
            receipt = {"status": "DRY_RUN_NOT_UPLOADED"}
            self.ledger.mark(cfg.phase, row.id, "dry_run")
        self._commit(ctx, decision)
        return self._record({"status": "SUBMITTED" if cfg.mode == "live" else cfg.mode.upper(), "round_id": row.id,
                             "receipt_status": receipt.get("status"), "trace": str(trace_path)})

    def run(self, *, max_seconds: float, sleep: Callable[[float], None] = time.sleep) -> list[dict[str, Any]]:
        start = time.monotonic()
        while time.monotonic() - start < max_seconds:
            self.step()
            sleep(self.config.poll_seconds)
        return self.log

    def _commit(self, ctx: DecisionContext, decision: Any) -> None:
        self.agent.commit(ctx, self.state, decision)
        self.state.save(self.config.state_path)

    def _record(self, item: dict[str, Any]) -> dict[str, Any]:
        self.log.append(item)
        return item


class LocalPaperSession:
    """In-process stand-in for the organizer service (rehearsals and tests).

    Mirrors the documented semantics: first in-window attempt consumes the
    slot; missing decision holds; the portfolio is reported as cash + shares.
    Execution is not simulated here (use the backtester for P&L).
    """

    def __init__(self, schedule_payload: dict[str, Any], clock: Callable[[], datetime],
                 portfolio: PortfolioState | None = None) -> None:
        self._schedule = schedule_payload
        self._clock = clock
        self._portfolio = portfolio or PortfolioState.initial()
        self.uploads: list[dict[str, Any]] = []

    def schedule(self) -> dict[str, Any]:
        return {**self._schedule, "current_time": self._clock().isoformat()}

    def portfolio(self, phase: str = "validation") -> dict[str, Any]:
        p = self._portfolio
        return {"cash": p.cash, "positions": {s: {"shares": q} for s, q in zip(SYMBOLS, p.shares, strict=True) if q}}

    def round(self, round_id: str) -> dict[str, Any]:
        return {"decisions": [u for u in self.uploads if u["round_id"] == round_id]}

    def decision(self, path: str | Path) -> dict[str, Any]:
        import json

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        rid = payload["round_id"]
        status = "DUPLICATE" if any(u["round_id"] == rid for u in self.uploads) else "PENDING"
        self.uploads.append({"round_id": rid, "selection_status": "SELECTED" if status == "PENDING" else "DUPLICATE",
                             "weights_sum": float(np.sum(list(payload["weights"].values())))})
        return {"status": status, "round_id": rid}
