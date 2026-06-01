"""Convenience helpers for batched grid-style backtests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from nlpcc.execution.order_planner import OrderPlannerConfig
from tools.backtesting.cuda_vectorized_backtester import (
    BatchedOfficialSemanticsInput,
    BatchedOfficialSemanticsResult,
    run_batched_official_semantics,
)
from tools.backtesting.reference_official_semantics import load_official_semantics_arrays


@dataclass(frozen=True)
class WeightCandidate:
    name: str
    weights: dict[str, float]


def constant_weight_tensor(
    candidates: Iterable[WeightCandidate],
    *,
    dates: tuple[str, ...],
    assets: tuple[str, ...],
) -> tuple[tuple[str, ...], np.ndarray]:
    names: list[str] = []
    rows: list[np.ndarray] = []
    for candidate in candidates:
        names.append(candidate.name)
        row = np.array([max(0.0, float(candidate.weights.get(asset, 0.0))) for asset in assets], dtype=float)
        rows.append(np.tile(row, (len(dates), 1)))
    if not rows:
        raise ValueError("At least one candidate is required.")
    return tuple(names), np.stack(rows, axis=0)


def run_constant_weight_grid(
    *,
    data_root: Path,
    track: str,
    candidates: Iterable[WeightCandidate],
    start_date: str | None = None,
    end_date: str | None = None,
    max_dates: int | None = None,
    planner_config: OrderPlannerConfig | None = None,
    backend: str = "auto",
    prefer_cuda: bool = True,
) -> BatchedOfficialSemanticsResult:
    dates, assets, open_prices, pct_changes = load_official_semantics_arrays(
        data_root,
        track,  # type: ignore[arg-type]
        start_date=start_date,
        end_date=end_date,
        max_dates=max_dates,
    )
    names, target_weights = constant_weight_tensor(candidates, dates=dates, assets=assets)
    return run_batched_official_semantics(
        BatchedOfficialSemanticsInput(
            dates=dates,
            assets=assets,
            open_prices=open_prices,
            pct_changes=pct_changes,
            target_weights=target_weights,
            candidate_names=names,
            planner_config=planner_config or OrderPlannerConfig(),
        ),
        backend=backend,
        prefer_cuda=prefer_cuda,
    )


def summarize_batched_result(result: BatchedOfficialSemanticsResult) -> list[dict[str, Any]]:
    return [
        {
            "name": candidate.name,
            "final_value": candidate.final_value,
            "metrics": candidate.metrics,
            "backend": result.backend,
            "device": result.device,
        }
        for candidate in result.candidates
    ]
