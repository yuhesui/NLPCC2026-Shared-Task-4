"""Seeded random-search helper."""

from __future__ import annotations

from typing import Any, Callable

from tools.optimiser.search_space import SearchSpace


Objective = Callable[[dict[str, Any]], dict[str, Any]]


def run_random_search(search_space: SearchSpace, objective: Objective, *, count: int, seed: int = 0) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for params in search_space.sample(count=count, seed=seed):
        outcome = objective(params)
        results.append({"params": params, **outcome})
    return results
