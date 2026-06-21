"""Deterministic return-correlation graph features."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class CorrelationGraphEdge:
    left: str
    right: str
    correlation: float

    def as_dict(self) -> dict[str, float | str]:
        return {"left": self.left, "right": self.right, "correlation": self.correlation}


def pearson_correlation(left: tuple[float, ...] | list[float], right: tuple[float, ...] | list[float]) -> float:
    length = min(len(left), len(right))
    if length < 2:
        return 0.0
    x = tuple(float(value) for value in left[-length:])
    y = tuple(float(value) for value in right[-length:])
    mean_x = sum(x) / length
    mean_y = sum(y) / length
    cov = sum((x[idx] - mean_x) * (y[idx] - mean_y) for idx in range(length))
    var_x = sum((value - mean_x) ** 2 for value in x)
    var_y = sum((value - mean_y) ** 2 for value in y)
    denom = sqrt(var_x * var_y)
    return 0.0 if denom <= 0 else max(-1.0, min(1.0, cov / denom))


def build_correlation_graph(
    returns_by_fund: dict[str, tuple[float, ...] | list[float]],
    *,
    threshold: float = 0.45,
    max_edges_per_asset: int = 3,
) -> tuple[CorrelationGraphEdge, ...]:
    funds = tuple(sorted(returns_by_fund))
    candidates: list[CorrelationGraphEdge] = []
    for left_index, left in enumerate(funds):
        for right in funds[left_index + 1 :]:
            corr = pearson_correlation(returns_by_fund[left], returns_by_fund[right])
            if abs(corr) >= threshold:
                candidates.append(CorrelationGraphEdge(left=left, right=right, correlation=round(corr, 8)))
    candidates.sort(key=lambda edge: (-abs(edge.correlation), edge.left, edge.right))
    counts = {fund_id: 0 for fund_id in funds}
    selected: list[CorrelationGraphEdge] = []
    for edge in candidates:
        if counts[edge.left] >= max_edges_per_asset or counts[edge.right] >= max_edges_per_asset:
            continue
        selected.append(edge)
        counts[edge.left] += 1
        counts[edge.right] += 1
    return tuple(sorted(selected, key=lambda edge: (edge.left, edge.right)))
