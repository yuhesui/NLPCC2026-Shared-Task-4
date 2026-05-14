"""Deterministic random constrained baseline."""

from __future__ import annotations

import random
from typing import Sequence

from nlpcc4.execution.constraints import project_long_only


def random_constrained_targets(
    fund_pool: Sequence[str],
    *,
    seed: int = 7,
    decision_date: str = "",
    cash_buffer: float = 0.0,
    max_weight: float | None = None,
) -> dict[str, float]:
    """Return deterministic pseudo-random long-only targets."""
    rng = random.Random(f"{seed}:{decision_date}:{','.join(fund_pool)}")
    raw = {asset: rng.random() for asset in fund_pool}
    return project_long_only(raw, universe=fund_pool, cash_buffer=cash_buffer, max_weight=max_weight)
