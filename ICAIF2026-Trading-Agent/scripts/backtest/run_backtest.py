#!/usr/bin/env python3
"""Backtest one system config over a data config, without registering.

  python scripts/backtest/run_backtest.py configs/systems/q3_shrinkage_erc.yaml --data configs/data/synthetic_default.yaml
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from icaif.backtest.engine import BacktestConfig, run_backtest
from icaif.competition.schedule import generate_standard_schedule
from icaif.core.config import load_config
from icaif.experiments.runner import load_data
from icaif.runtime.agent import build_agent


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("system")
    p.add_argument("--data", default="configs/data/synthetic_default.yaml")
    p.add_argument("--warmup-days", type=int, default=20)
    p.add_argument("--traces", default="")
    args = p.parse_args()
    panel, _, manifest = load_data(load_config(args.data))
    days = panel.trading_days()[args.warmup_days:]
    schedule = generate_standard_schedule("validation", days)
    cfg = BacktestConfig(trace_dir=Path(args.traces) if args.traces else None)
    result = run_backtest(panel, build_agent(load_config(args.system)), schedule, "validation", config=cfg)
    print(json.dumps({**result.as_dict(), "dataset": manifest["name"]}, indent=2, default=str))
    if result.synthetic_data:
        print("NOTE: synthetic data - plumbing check only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
