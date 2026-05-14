"""Convert bounded scores into target-weight proposals."""

from __future__ import annotations

from typing import Mapping, Sequence

from nlpcc4.execution.constraints import project_long_only


def score_to_weight_targets(
    scores: Mapping[str, float],
    *,
    universe: Sequence[str] | None = None,
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
    long_only_shift: bool = True,
) -> dict[str, float]:
    """Convert bounded scores to long-only target weights."""
    keys = tuple(universe) if universe is not None else tuple(scores.keys())
    if long_only_shift:
        min_score = min((scores.get(asset, 0.0) for asset in keys), default=0.0)
        raw = {asset: max(0.0, float(scores.get(asset, 0.0)) - min_score) for asset in keys}
    else:
        raw = {asset: max(0.0, float(scores.get(asset, 0.0))) for asset in keys}
    if sum(raw.values()) <= 0:
        raw = {asset: 1.0 for asset in keys}
    return project_long_only(raw, universe=keys, cash_buffer=cash_buffer, max_weight=max_weight)
