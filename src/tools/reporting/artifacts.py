"""Artifact writing helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_artifact_dir(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_json_artifact(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return path


def write_text_artifact(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
