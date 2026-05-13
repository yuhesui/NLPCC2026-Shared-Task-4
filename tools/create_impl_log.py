#!/usr/bin/env python3
"""Create timestamped implementation logs in the canonical reports directory."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("docs/reports/implementation_logs")


def sanitize_title(title: str) -> str:
    """Convert a short title to a safe filename component."""
    sanitized = "".join(char if char.isalnum() else "_" for char in title.strip())
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    return sanitized.strip("_").lower()


def create_impl_log(title: str, output_dir: str | Path | None = None) -> Path:
    """Create a timestamped implementation log from the standard template."""
    if not title or not title.strip():
        raise ValueError("title cannot be empty")

    target_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filename = f"{now:%Y%m%d_%H%M}_{sanitize_title(title)}.md"
    path = target_dir / filename
    if path.exists():
        raise FileExistsError(f"implementation log already exists: {path}")

    path.write_text(
        f"""# {title}

**Date:** {now:%Y-%m-%d}
**Time:** {now:%H:%M}
**Scope:** Repository initialization
**Repository:** NLPCC2026-Shared-Task-4

## Summary of Changes

TBD

## Read-First Evidence Table

| File | Exists? | Key facts extracted | Implications for init | Action needed |
| --- | --- | --- | --- | --- |

## Repository Inspection Result

TBD

## Files Created

TBD

## Files Modified

TBD

## Files Intentionally Not Touched

TBD

## Verification Commands Run

TBD

## Verification Results

TBD

## Issues Found

TBD

## Must Fix Before Real Implementation

TBD

## Self-Review Checklist

- [ ] Official starter kit preserved under `NLPCC_tasks/`.
- [ ] Custom code separated under `src/nlpcc4/`.
- [ ] Strategy contract outputs target weights before trade conversion.
- [ ] Runtime artifacts and secrets ignored by Git.
- [ ] No full trading strategy, fake backtest, fake metrics, or fake LLM output added.
- [ ] Lightweight verification completed.

## Final Readiness Status

TBD
""",
        encoding="utf-8",
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("title", help="Short log title, e.g. 'repo init'.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Optional output directory. Defaults to docs/reports/implementation_logs.",
    )
    args = parser.parse_args()
    path = create_impl_log(args.title, args.output_dir)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
