#!/usr/bin/env python3
"""Validate a decision.json with BOTH our validator and the official kit's.

  python scripts/validation/validate_decision.py private/decisions/validation/<round>/decision.json \
      [--schedule live-schedule.json] [--submitted-at 2026-10-08T09:05:00-04:00]
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

from icaif.competition.official_adapter import OfficialKitUnavailable, load_official_kit
from icaif.competition.schedule import Schedule
from icaif.competition.submission import SubmissionValidationError, validate_decision_payload
from icaif.core.time import parse_timestamp


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path")
    p.add_argument("--schedule")
    p.add_argument("--submitted-at")
    args = p.parse_args()
    raw = Path(args.path).read_text(encoding="utf-8")
    payload = json.loads(raw, parse_float=Decimal)
    schedule = Schedule.from_official(json.loads(Path(args.schedule).read_text())) if args.schedule else None
    try:
        validate_decision_payload(payload, schedule=schedule,
                                  submitted_at=parse_timestamp(args.submitted_at) if args.submitted_at else None)
        print("icaif validator: OK")
    except SubmissionValidationError as error:
        print(f"icaif validator: INVALID ({error})", file=sys.stderr)
        return 2
    try:
        kit = load_official_kit()
        kit.validate_decision_file(Path(args.path), schedule_path=Path(args.schedule) if args.schedule else None,
                                   submitted_at=args.submitted_at)
        print("official validator: OK")
    except OfficialKitUnavailable as error:
        print(f"official validator: SKIPPED ({error})", file=sys.stderr)
        return 3
    except ValueError as error:
        print(f"official validator: INVALID ({error})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
