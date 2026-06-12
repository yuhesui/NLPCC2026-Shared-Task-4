#!/usr/bin/env python
"""Compile src and tests in memory without writing __pycache__ files."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    roots = (Path("src"), Path("tests"))
    bad: list[tuple[str, str, str]] = []
    count = 0
    for root in roots:
        for path in root.rglob("*.py"):
            count += 1
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except Exception as exc:  # pragma: no cover - command line smoke.
                bad.append((str(path), type(exc).__name__, str(exc)))
    print(f"files_checked {count}")
    print(f"bad_count {len(bad)}")
    for path, kind, message in bad[:20]:
        print(f"{path}: {kind}: {message}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
