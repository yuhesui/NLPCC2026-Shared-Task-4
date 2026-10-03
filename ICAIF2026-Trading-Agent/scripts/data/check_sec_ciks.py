#!/usr/bin/env python3
"""Verify the hard-coded CIK map against SEC company_tickers.json (network, opt-in).

  SEC_USER_AGENT="Your Name you@example.org" python scripts/data/check_sec_ciks.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

from icaif.data.sec.edgar import CIKS


def main() -> int:
    agent = os.environ.get("SEC_USER_AGENT", "")
    if "@" not in agent:
        print("set SEC_USER_AGENT='Name email'", file=sys.stderr)
        return 2
    req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json", headers={"User-Agent": agent})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    official = {row["ticker"]: str(row["cik_str"]).zfill(10) for row in data.values()}
    bad = {t: (c, official.get(t)) for t, c in CIKS.items() if official.get(t) != c}
    print("all CIKs match" if not bad else f"MISMATCHES: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
