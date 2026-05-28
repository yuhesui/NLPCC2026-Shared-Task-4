"""Grid-search helper."""

from __future__ import annotations

from typing import Any, Callable

from tools.optimiser.search_space import SearchSpace


Objective = Callable[[dict[str, Any]], dict[str, Any]]


def run_grid_search(search_space: SearchSpace, objective: Objective) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for params in search_space.grid():
        outcome = objective(params)
        results.append({"params": params, **outcome})
    return results
