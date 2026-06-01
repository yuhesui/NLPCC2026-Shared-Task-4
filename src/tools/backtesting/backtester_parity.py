"""Parity helpers for reference and batched official-semantics backtesters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.backtesting.cuda_vectorized_backtester import CandidateBacktestResult
from tools.backtesting.reference_official_semantics import OfficialSemanticsResult


@dataclass(frozen=True)
class BacktesterParityResult:
    max_value_diff: float
    final_value_diff: float
    metric_diffs: dict[str, float]
    within_tolerance: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_value_diff": self.max_value_diff,
            "final_value_diff": self.final_value_diff,
            "metric_diffs": self.metric_diffs,
            "within_tolerance": self.within_tolerance,
        }


def compare_reference_to_candidate(
    reference: OfficialSemanticsResult,
    candidate: CandidateBacktestResult,
    *,
    tolerance: float = 1e-6,
) -> BacktesterParityResult:
    ref_values = list(reference.portfolio_values)
    cand_values = list(candidate.portfolio_values)
    common = min(len(ref_values), len(cand_values))
    value_diffs = [abs(ref_values[index] - cand_values[index]) for index in range(common)]
    if len(ref_values) != len(cand_values):
        value_diffs.append(float("inf"))
    metric_names = sorted(set(reference.metrics) | set(candidate.metrics))
    metric_diffs = {
        name: abs(float(reference.metrics.get(name, 0.0)) - float(candidate.metrics.get(name, 0.0)))
        for name in metric_names
    }
    final_diff = abs(float(reference.final_value) - float(candidate.final_value))
    max_value_diff = max(value_diffs or [0.0])
    within = final_diff <= tolerance and max_value_diff <= tolerance and all(diff <= tolerance for diff in metric_diffs.values())
    return BacktesterParityResult(
        max_value_diff=max_value_diff,
        final_value_diff=final_diff,
        metric_diffs=metric_diffs,
        within_tolerance=within,
    )
