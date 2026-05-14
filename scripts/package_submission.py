#!/usr/bin/env python3
"""Package source/config files for a reproducible submission draft."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from nlpcc4.common.paths import runtime_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--llm-mode", choices=["off", "manual", "api"], default="off")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else runtime_root() / "submissions"
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"{args.track}_{args.strategy}_submission_draft.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for root in ("src", "scripts", "configs", "docs/reports/phase_1a"):
            for path in Path(root).rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    archive.write(path, path.as_posix())
        archive.write(args.config, Path(args.config).as_posix())
    print(zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
