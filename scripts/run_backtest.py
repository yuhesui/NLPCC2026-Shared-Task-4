#!/usr/bin/env python3
"""Alias for running one local strategy backtest."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_strategy import main


if __name__ == "__main__":
    raise SystemExit(main())
