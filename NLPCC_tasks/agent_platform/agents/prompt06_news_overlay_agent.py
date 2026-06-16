"""Prompt06 thin official-facing adapter for precomputed research candidates.

This module is not a default official runtime. It is used only by Prompt06 local
replay evidence to pass candidate weights through the starter-kit agent shape.
"""

from __future__ import annotations

import asyncio
import csv
from pathlib import Path
from typing import Any


class Prompt06PrecomputedTargetAgent:
    """Return precomputed target weights through the official agent API."""

    def __init__(self, *, candidate_id: str, target_weights_csv: str | Path) -> None:
        self.candidate_id = candidate_id
        self.target_weights_csv = Path(target_weights_csv)
        self.targets = self._load_targets(self.target_weights_csv)

    def decide(
        self,
        *,
        date_to_decision: str | int | None = None,
        fund_pool: list[str] | tuple[str, ...] | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        date_key = str(date_to_decision).replace("-", "")
        weights = dict(self.targets.get(date_key, {}))
        if fund_pool is not None:
            allowed = {str(item) for item in fund_pool}
            weights = {fund_id: weight for fund_id, weight in weights.items() if fund_id in allowed}
        return {
            "target_weights": weights,
            "trades": [],
            "reasoning": "Prompt06 local official-facing replay of precomputed research target weights.",
            "metadata": {
                "agent": "Prompt06PrecomputedTargetAgent",
                "candidate_id": self.candidate_id,
                "target_weights_csv": str(self.target_weights_csv),
                "official_server_run": False,
                "official_runtime_default": False,
            },
        }

    async def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        final_decision = self.decide(**kwargs)
        await asyncio.sleep(0)
        return {"final_decision": final_decision}

    @staticmethod
    def _load_targets(path: Path) -> dict[str, dict[str, float]]:
        targets: dict[str, dict[str, float]] = {}
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                date_key = str(row["date"]).replace("-", "")
                fund_id = str(row["fund_id"])
                targets.setdefault(date_key, {})[fund_id] = float(row["target_weight"])
        return targets
