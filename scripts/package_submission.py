#!/usr/bin/env python3
"""Build a clean candidate submission package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from tools.verification.submission_package import audit_submission_archive, build_submission_package  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package candidate code/config artifacts without raw data.")
    parser.add_argument("--output-root", default=str(REPO_ROOT / "outputs" / "submissions"))
    parser.add_argument("--package-name", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_submission_package(
        repo_root=REPO_ROOT,
        output_root=Path(args.output_root),
        package_name=args.package_name,
    )
    audit = audit_submission_archive(result.archive_path)
    payload = {"status": "ok" if not audit["issues"] else "failed", "package": result.as_dict(), "archive_audit": audit}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not audit["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
