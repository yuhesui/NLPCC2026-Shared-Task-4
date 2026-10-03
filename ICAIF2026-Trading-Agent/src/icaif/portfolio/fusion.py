"""Bounded signal overlay:  w_base -> s -> Δw -> w_target.

Preserves AlphaAllocator's central idea — text perturbs a robust quantitative
portfolio rather than allocating capital — with the improvements requested for
ICAIF:

* Δw is exactly zero-sum (``1'Δw = 0``) before feasibility repair, and the
  L1 budget ``||Δw||_1 <= eta_t`` is enforced;
* ``eta_t`` can depend on confidence, event type, volatility or regime;
* several score transforms (linear, rank, softmax, sigmoid, clipped z-score,
  sparse top-k) are interchangeable;
* the result is re-projected onto the ICAIF feasible set at the *base* gross,
  and the realised overlay (after repair) is reported.

Overlay scores may be any finite real numbers; NaN means "no information" and
maps to zero tilt.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from icaif.features.cross_sectional import rank_score, zscore
from icaif.portfolio.constraints import Constraints, project_capped_simplex

TRANSFORMS = ("linear", "rank", "softmax", "sigmoid", "zscore", "topk")


def transform_scores(s: np.ndarray, method: str, *, temperature: float = 1.0, k: int = 5, clip: float = 3.0) -> np.ndarray:
    """Map raw scores to a zero-mean direction vector (NaN -> no tilt)."""

    s = np.asarray(s, dtype=float)
    info = np.isfinite(s)
    out = np.zeros_like(s)
    if info.sum() == 0:
        return out
    x = np.where(info, s, 0.0)
    if method == "linear":
        d = x
    elif method == "rank":
        d = np.nan_to_num(rank_score(np.where(info, s, np.nan)))
    elif method == "zscore":
        d = np.nan_to_num(zscore(np.where(info, s, np.nan), clip=clip))
    elif method == "sigmoid":
        d = 2.0 / (1.0 + np.exp(-x / max(temperature, 1e-9))) - 1.0
    elif method == "softmax":
        z = x[info] / max(temperature, 1e-9)
        p = np.exp(z - z.max())
        d = np.zeros_like(x)
        d[info] = p / p.sum()
    elif method == "topk":
        order = np.argsort(-np.where(info, x, -np.inf), kind="mergesort")
        bottom = np.argsort(np.where(info, x, np.inf), kind="mergesort")
        d = np.zeros_like(x)
        top = [i for i in order[:k] if info[i] and x[i] > 0]
        bot = [i for i in bottom[:k] if info[i] and x[i] < 0]
        d[top] = 1.0
        d[bot] = -1.0
    else:
        raise ValueError(f"unknown transform {method!r}; choose from {TRANSFORMS}")
    d = np.where(info, d, 0.0)
    if info.sum() > 0:
        d[info] -= d[info].mean()
    out = d
    if np.abs(out).sum() < 1e-15:
        return np.zeros_like(out)
    return out


def overlay_budget(config: Mapping[str, Any], *, confidence: float = 1.0, event_multiplier: float = 1.0,
                   vol_ratio: float = 1.0, regime_multiplier: float = 1.0) -> tuple[float, dict[str, float]]:
    """eta_t = cap * f(confidence) * event * vol * regime   (each switchable).

    ``vol_ratio`` = current vol / long-run vol (higher vol -> smaller overlay).
    """

    cap = float(config.get("cap", 0.0))
    parts = {"cap": cap}
    mode = config.get("modes", ())
    eta = cap
    if "confidence" in mode:
        parts["confidence"] = float(np.clip(confidence, 0.0, 1.0))
        eta *= parts["confidence"]
    if "event" in mode:
        parts["event"] = float(max(0.0, event_multiplier))
        eta *= parts["event"]
    if "volatility" in mode:
        parts["volatility"] = float(1.0 / max(vol_ratio, 1e-6)) if vol_ratio > 1 else 1.0
        eta *= parts["volatility"]
    if "regime" in mode:
        parts["regime"] = float(np.clip(regime_multiplier, 0.0, 1.0))
        eta *= parts["regime"]
    if config.get("max_cap") is not None:
        eta = min(eta, float(config["max_cap"]))
    return max(0.0, eta), parts


@dataclass
class OverlayResult:
    weights: np.ndarray
    intended_delta: np.ndarray
    realised_delta: np.ndarray
    eta: float
    diagnostics: dict[str, Any] = field(default_factory=dict)


def apply_overlay(
    base: np.ndarray,
    scores: np.ndarray,
    *,
    eta: float,
    transform: str = "zscore",
    cons: Constraints | None = None,
    per_asset_cap: float | None = None,
    deadband: float = 0.0,
    temperature: float = 1.0,
    k: int = 5,
) -> OverlayResult:
    cons = cons or Constraints()
    base = np.asarray(base, dtype=float)
    gross = float(base.sum())
    direction = transform_scores(scores, transform, temperature=temperature, k=k)
    if eta <= 0 or not np.any(direction):
        return OverlayResult(base.copy(), np.zeros_like(base), np.zeros_like(base), 0.0, {"skipped": True})
    delta = direction / np.abs(direction).sum() * eta  # ||Δ||_1 = eta, sum Δ = 0
    if per_asset_cap is not None:
        delta = balance_zero_sum(np.clip(delta, -per_asset_cap, per_asset_cap))
    if deadband > 0:
        delta = balance_zero_sum(np.where(np.abs(delta) < deadband, 0.0, delta))
    target = project_capped_simplex(base + delta, cons.max_weight, min(gross, cons.max_gross))
    realised = target - base
    return OverlayResult(
        weights=target,
        intended_delta=delta,
        realised_delta=realised,
        eta=eta,
        diagnostics={
            "intended_l1": float(np.abs(delta).sum()),
            "realised_l1": float(np.abs(realised).sum()),
            "intended_sum": float(delta.sum()),
            "gross": float(target.sum()),
        },
    )


def balance_zero_sum(delta: np.ndarray) -> np.ndarray:
    """Restore sum(delta) == 0 by shrinking the larger side (never grows any entry,
    so per-asset caps and the L1 budget remain satisfied)."""

    pos = delta[delta > 0].sum()
    neg = -delta[delta < 0].sum()
    if pos <= 0 or neg <= 0:
        return np.zeros_like(delta)
    out = delta.copy()
    if pos > neg:
        out[out > 0] *= neg / pos
    else:
        out[out < 0] *= pos / neg
    return out
