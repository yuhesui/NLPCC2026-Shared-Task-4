"""Small cross-validation orchestration primitives."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from tools.optimiser.five_fold_split import FiveFoldSplit
from tools.optimiser.scorer import score_metrics


FoldObjective = Callable[[dict[str, Any], FiveFoldSplit], dict[str, Any]]


def run_cross_validation(
    *,
    candidates: Iterable[dict[str, Any]],
    folds: Iterable[FiveFoldSplit],
    objective: FoldObjective,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for params in candidates:
        fold_scores: list[float] = []
        fold_rows: list[dict[str, Any]] = []
        for fold in folds:
            outcome = objective(params, fold)
            metrics = dict(outcome.get("metrics", {}) or {})
            score = score_metrics(metrics)
            fold_scores.append(score)
            fold_rows.append({"fold": fold.fold, "score": score, "metrics": metrics, "status": outcome.get("status", "ok")})
        rows.append(
            {
                "params": dict(params),
                "folds": fold_rows,
                "mean_score": sum(fold_scores) / len(fold_scores) if fold_scores else 0.0,
                "fold_count": len(fold_rows),
            }
        )
    rows.sort(key=lambda item: (-float(item["mean_score"]), str(item["params"])))
    return rows
