"""Utilities for comparing local and official backtest summaries."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Mapping


DEFAULT_TOLERANCES: dict[str, float] = {
    "cumulative_return": 1e-8,
    "annualized_volatility": 1e-8,
    "sharpe_ratio": 1e-8,
    "max_drawdown": 1e-8,
    "turnover": 1e-8,
}


@dataclass(frozen=True)
class MetricDifference:
    metric: str
    official: float | None
    local: float | None
    difference: float | None
    tolerance: float
    within_tolerance: bool


@dataclass(frozen=True)
class ComparisonResult:
    differences: tuple[MetricDifference, ...]

    @property
    def ok(self) -> bool:
        return all(item.within_tolerance for item in self.differences)

    def as_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "differences": [item.__dict__ for item in self.differences],
        }


def compare_metric_dicts(
    official: Mapping[str, float],
    local: Mapping[str, float],
    tolerances: Mapping[str, float] | None = None,
) -> ComparisonResult:
    configured = {**DEFAULT_TOLERANCES, **(dict(tolerances or {}))}
    metrics = sorted(set(official) | set(local) | set(configured))
    differences: list[MetricDifference] = []
    for metric in metrics:
        official_value = official.get(metric)
        local_value = local.get(metric)
        tolerance = configured.get(metric, 0.0)
        if official_value is None or local_value is None:
            difference = None
            within = official_value == local_value
        else:
            difference = float(local_value) - float(official_value)
            within = abs(difference) <= tolerance
        differences.append(
            MetricDifference(
                metric=metric,
                official=official_value,
                local=local_value,
                difference=difference,
                tolerance=tolerance,
                within_tolerance=within,
            )
        )
    return ComparisonResult(tuple(differences))


def compare_result_files(
    official_path: Path,
    local_path: Path,
    tolerances: Mapping[str, float] | None = None,
) -> ComparisonResult:
    official = json.loads(official_path.read_text(encoding="utf-8"))
    local = json.loads(local_path.read_text(encoding="utf-8"))
    return compare_metric_dicts(official.get("metrics", official), local.get("metrics", local), tolerances)
