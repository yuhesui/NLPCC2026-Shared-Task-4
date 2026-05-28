"""Deterministic JSON result store."""

from __future__ import annotations

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

    def write(self, name: str, result: dict[str, Any]) -> Path:
        path = self.path_for(name)
        path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return path

    def read(self, name: str) -> dict[str, Any]:
        return json.loads(self.path_for(name).read_text(encoding="utf-8"))

    def list_results(self) -> list[str]:
        return sorted(path.stem for path in self.root.glob("*.json"))
