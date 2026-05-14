"""Result parsing helpers for local and official runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_metrics(path: str | Path) -> dict[str, Any]:
    """Load a metrics JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_diagnostics(path: str | Path) -> dict[str, Any]:
    """Load a diagnostics JSON file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
