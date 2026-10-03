"""Final target finalisation: fee buffer, feasibility, exact validation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.core.constants import FEE_RATE
from icaif.core.universe import SYMBOLS
from icaif.portfolio.constraints import Constraints, constraint_violations, project_to_feasible
from icaif.portfolio.turnover import l1_turnover


class InvalidTargetError(ValueError):
    pass


@dataclass(frozen=True)
class FinalTarget:
    weights: np.ndarray
    gross: float
    expected_turnover: float
    fee_buffer: float


def finalize_target(
    target: np.ndarray, current: np.ndarray, cons: Constraints | None = None, *, fee_rate: float = FEE_RATE
) -> FinalTarget:
    """Project onto the feasible set leaving cash for the rebalance fee.

    The fee is paid from the account, so a fully invested target (sum = 1)
    would leave negative cash after fees. We cap gross at
    ``1 - fee_rate * turnover`` (organizer behaviour on tolerated excess is not
    documented; see docs/competition/ICAIF_RULES_AND_PROTOCOL.md, open question Q3).
    """

    cons = cons or Constraints()
    target = np.asarray(target, dtype=float)
    if target.shape != (len(SYMBOLS),):
        raise InvalidTargetError(f"target must have shape ({len(SYMBOLS)},)")
    if not np.isfinite(target).all():
        raise InvalidTargetError("target contains non-finite values")
    turnover = l1_turnover(target, current)
    buffer = fee_rate * turnover
    max_gross = min(cons.max_gross, 1.0 - buffer)
    w = project_to_feasible(target, cons, gross=max_gross) if target.sum() > max_gross or (target < 0).any() or (
        target > cons.max_weight).any() else target.copy()
    w = np.where(w < 1e-10, 0.0, w)
    issues = constraint_violations(w, cons)
    if issues:
        raise InvalidTargetError(",".join(issues))
    return FinalTarget(w, float(w.sum()), l1_turnover(w, current), buffer)


def to_weight_dict(w: np.ndarray) -> dict[str, float]:
    return {s: float(x) for s, x in zip(SYMBOLS, w, strict=True)}


def from_weight_dict(d: dict[str, float]) -> np.ndarray:
    return np.array([float(d[s]) for s in SYMBOLS])
