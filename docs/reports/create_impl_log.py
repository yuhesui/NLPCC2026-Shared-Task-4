#!/usr/bin/env python3
"""Compatibility wrapper for the canonical implementation-log generator.

The canonical script is `tools/create_impl_log.py`. This wrapper remains here
only so older local notes that reference `docs/reports/create_impl_log.py` do
not silently create logs in the wrong directory.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.create_impl_log import create_impl_log, main, sanitize_title  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())

