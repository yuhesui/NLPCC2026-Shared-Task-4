"""Deterministic successive-halving helper."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


ResourceObjective = Callable[[dict[str, Any], int], dict[str, Any]]


@dataclass(frozen=True)
class HalvingRound:
    round_index: int
    resource: int
    evaluated: int
    retained: int
    rows: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "round_index": self.round_index,
            "resource": self.resource,
            "evaluated": self.evaluated,
            "retained": self.retained,
            "rows": list(self.rows),
        }


def run_successive_halving(
    candidates: Iterable[dict[str, Any]],
    objective: ResourceObjective,
    *,
    min_resource: int,
    max_rounds: int = 3,
    reduction_factor: int = 2,
) -> tuple[HalvingRound, ...]:
    active = [dict(candidate) for candidate in candidates]
    if not active:
        return ()
    if min_resource <= 0 or reduction_factor < 2 or max_rounds <= 0:
        raise ValueError("min_resource, reduction_factor, and max_rounds must be positive.")
    rounds: list[HalvingRound] = []
    resource = min_resource
    for round_index in range(1, max_rounds + 1):
        rows = []
        for params in active:
            outcome = objective(params, resource)
            rows.append({"params": params, **outcome})
        rows.sort(key=lambda item: (-float(item.get("score", 0.0)), str(item.get("params", {}))))
        retained_count = max(1, len(rows) // reduction_factor)
        active = [dict(row["params"]) for row in rows[:retained_count]]
        rounds.append(
            HalvingRound(
                round_index=round_index,
                resource=resource,
                evaluated=len(rows),
                retained=retained_count,
                rows=tuple(rows),
            )
        )
        if len(active) <= 1:
            break
        resource *= reduction_factor
    return tuple(rounds)
