"""Deterministic JSON result store."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ResultStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, name: str) -> Path:
        safe = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in name)
        return self.root / f"{safe}.json"

    @staticmethod
    def payload_hash(payload: dict[str, Any]) -> str:
        material = json.dumps(payload, indent=None, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]

    def write(self, name: str, result: dict[str, Any]) -> Path:
        path = self.path_for(name)
        payload = dict(result)
        payload.setdefault("result_hash", self.payload_hash(result))
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return path

    def read(self, name: str) -> dict[str, Any]:
        return json.loads(self.path_for(name).read_text(encoding="utf-8"))

    def list_results(self) -> list[str]:
        return sorted(path.stem for path in self.root.glob("*.json"))
