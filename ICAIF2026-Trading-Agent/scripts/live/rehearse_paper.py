#!/usr/bin/env python3
"""Offline rehearsal of the full live loop on SYNTHETIC data with a simulated clock.

Exercises: schedule polling, active-round detection, AS_OF freezing, agent decision, decision traces,
dual validation, ledger idempotency and one-upload-per-round against LocalPaperSession.

  python scripts/live/rehearse_paper.py --system configs/systems/q3_shrinkage_erc.yaml
"""
from __future__ import annotations

import argparse
import tempfile
from datetime import timedelta
from pathlib import Path

from icaif.competition.schedule import generate_standard_schedule
from icaif.core.config import load_config
from icaif.core.universe import SYMBOLS
from icaif.data.market.synthetic import SyntheticConfig, generate_synthetic_world
from icaif.runtime.agent import build_agent
from icaif.runtime.context import PanelContextBuilder
from icaif.runtime.scheduler import LiveRunner, LocalPaperSession, RunnerConfig


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", default="configs/systems/q3_shrinkage_erc.yaml")
    p.add_argument("--days", type=int, default=2)
    args = p.parse_args()
    world = generate_synthetic_world(SyntheticConfig(days=30))
    days = world.panel.trading_days()[-args.days:]
    sched = generate_standard_schedule("validation", days)
    payload = {"symbols": list(SYMBOLS), "universe_confirmed": True, "rounds": [r.as_dict() for r in sched.rounds]}
    clock = {"t": sched.rounds[0].opens_at + timedelta(minutes=1)}
    session = LocalPaperSession(payload, lambda: clock["t"])
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        runner = LiveRunner(session, build_agent(load_config(args.system)), PanelContextBuilder(lambda: world.panel),
                            RunnerConfig("validation", "paper", root / "state.json", root / "ledger.jsonl",
                                         root / "traces", root / "private"), credentials=lambda: ("paper-team", "paper-token"))
        for row in sched.rounds:
            for offset in (5, 6):  # two polls per window: the second must be ALREADY_DECIDED
                clock["t"] = row.deadline - timedelta(minutes=offset + 3)
                print(runner.step())
        uploads = len(session.uploads)
    print(f"uploads={uploads} rounds={len(sched.rounds)} (holds do not upload)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
