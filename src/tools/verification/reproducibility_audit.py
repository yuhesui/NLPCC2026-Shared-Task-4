"""Reproducibility audit helpers."""

from __future__ import annotations

import hashlib
import platform
from pathlib import Path
import sys


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_files(paths: list[Path]) -> dict[str, str]:
    return {str(path): sha256_file(path) for path in sorted(paths)}


def runtime_fingerprint() -> dict[str, str]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
    }
