#!/usr/bin/env python3
"""Run one experiment config and register it.

  python scripts/experiments/run_experiment.py configs/experiments/smoke_q3_erc.yaml [--traces]
"""
from __future__ import annotations

import argparse
import json

from icaif.experiments.runner import run_experiment


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("config")
    p.add_argument("--traces", action="store_true", help="write per-round decision traces")
    args = p.parse_args()
    out = run_experiment(args.config, write_traces=args.traces)
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
