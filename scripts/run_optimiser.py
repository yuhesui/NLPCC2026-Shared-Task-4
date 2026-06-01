#!/usr/bin/env python3
"""Backward-compatible alias for scripts/run_optimisation.py."""

from __future__ import annotations

from run_optimisation import main


if __name__ == "__main__":
    raise SystemExit(main())
