#!/usr/bin/env python3
"""Persistent Validation/Official loop through the OFFICIAL client.

  # rehearsal against the real schedule/portfolio API, never uploads:
  python scripts/live/run_live.py --system configs/systems/q3_shrinkage_erc.yaml --bars data/raw/market/bars_30m.csv \
      --phase validation --mode dry_run --max-hours 8
  # real uploads (one per round, guarded by ledger + official checkpoint):
  python scripts/live/run_live.py ... --mode live --confirm-live-uploads

Needs: `pip install -e '.[live]'`, scripts/setup/fetch_official_kit.sh, .env with CODABENCH_TOKEN and
ICAIF_PROFILE, team credentials in .icaif/credentials.json (created by the official `register` or
`import-credentials` command). The market-data CSV must be refreshed by a separate, terms-reviewed data job
(TODO(data): no live market feed is bundled).
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from icaif.competition.official_adapter import load_official_kit, open_official_session
from icaif.core.config import REPO_ROOT, load_config
from icaif.data.market.loaders import load_panel_csv
from icaif.runtime.agent import build_agent
from icaif.runtime.context import PanelContextBuilder
from icaif.runtime.scheduler import LiveRunner, RunnerConfig


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--system", required=True)
    p.add_argument("--bars", required=True, nargs="+")
    p.add_argument("--bar-minutes", type=int, default=30)
    p.add_argument("--phase", choices=("validation", "official"), required=True)
    p.add_argument("--mode", choices=("dry_run", "live"), default="dry_run")
    p.add_argument("--confirm-live-uploads", action="store_true")
    p.add_argument("--live-config", default="configs/execution/live.yaml")
    p.add_argument("--max-hours", type=float, default=1.0)
    args = p.parse_args()
    if args.mode == "live" and not args.confirm_live_uploads:
        p.error("--mode live requires --confirm-live-uploads")
    kit = load_official_kit()
    kit.config.load_environment(REPO_ROOT / ".env")  # our .env, not the kit directory's
    live = load_config(args.live_config)["live"]
    token = os.environ.get("CODABENCH_TOKEN", "")
    profile = os.environ.get("ICAIF_PROFILE", "")
    if not token or not profile:
        p.error("set CODABENCH_TOKEN and ICAIF_PROFILE in .env")
    private = REPO_ROOT / ".icaif"
    session = open_official_session(profile_path=Path(profile), checkpoint=private / "checkpoint.json",
                                    credentials=private / "credentials.json", token=token)
    with session:
        def credentials() -> tuple[str, str]:
            creds = session._team()  # official client accessor; values are never logged
            return creds["team_id"], creds["team_token"]

        runner = LiveRunner(
            session=session,
            agent=build_agent(load_config(args.system)),
            builder=PanelContextBuilder(lambda: load_panel_csv([Path(b) for b in args.bars], bar_minutes=args.bar_minutes)),
            config=RunnerConfig(phase=args.phase, mode=args.mode, state_path=REPO_ROOT / live["state_path"],
                                ledger_path=REPO_ROOT / live["ledger_path"], trace_dir=REPO_ROOT / live["trace_dir"],
                                private_dir=REPO_ROOT / live["private_dir"],
                                safety_margin_seconds=float(live["safety_margin_seconds"]),
                                poll_seconds=float(live["poll_seconds"])),
            credentials=credentials,
        )
        for item in runner.run(max_seconds=args.max_hours * 3600):
            if item["status"] != "WAITING":
                print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
