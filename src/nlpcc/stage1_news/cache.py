"""Deterministic JSON cache for Stage 1 extraction outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def stage1_cache_key(payload: Any, *, version: str = "stage1_mvp_v1") -> str:
    encoded = json.dumps({"version": version, "payload": payload}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class Stage1JsonCache:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.path_for(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: dict[str, Any]) -> Path:
        path = self.path_for(key)
        path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str), encoding="utf-8")
        return path
