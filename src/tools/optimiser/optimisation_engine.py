"""Prompt16 optimisation engine facade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from tools.optimiser.cross_validation import FoldObjective, run_cross_validation
from tools.optimiser.five_fold_split import FiveFoldSplit
from tools.optimiser.grid_search import run_grid_search
from tools.optimiser.parameter_space import StrategyParameterSpace
from tools.optimiser.random_search import run_random_search
from tools.optimiser.scorer import rank_results
from tools.optimiser.successive_halving import ResourceObjective, run_successive_halving


Objective = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class OptimisationRunConfig:
    strategy: str
    mode: str = "grid"
    random_count: int = 8
    seed: int = 0


def run_parameter_optimisation(
    space: StrategyParameterSpace,
    objective: Objective,
    *,
    mode: str = "grid",
    random_count: int = 8,
    seed: int = 0,
) -> list[dict[str, Any]]:
    search_space = space.as_search_space()
    if mode == "grid":
        rows = run_grid_search(search_space, objective)
    elif mode == "random":
        rows = run_random_search(search_space, objective, count=random_count, seed=seed)
    else:
        raise ValueError("mode must be 'grid' or 'random'.")
    return rank_results(rows)


def run_five_fold_optimisation(
    space: StrategyParameterSpace,
    folds: tuple[FiveFoldSplit, ...],
    objective: FoldObjective,
    *,
    max_candidates: int | None = None,
) -> list[dict[str, Any]]:
    candidates = space.as_search_space().grid()
    if max_candidates is not None:
        candidates = candidates[: max(1, int(max_candidates))]
    return run_cross_validation(candidates=candidates, folds=folds, objective=objective)


def run_halving_optimisation(
    space: StrategyParameterSpace,
    objective: ResourceObjective,
    *,
    min_resource: int,
    max_rounds: int = 3,
    reduction_factor: int = 2,
) -> list[dict[str, Any]]:
    rounds = run_successive_halving(
        space.as_search_space().grid(),
        objective,
        min_resource=min_resource,
        max_rounds=max_rounds,
        reduction_factor=reduction_factor,
    )
    return [round_info.as_dict() for round_info in rounds]
