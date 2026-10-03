"""Uncertainty / agreement measures for aggregated text evidence."""

from __future__ import annotations

import numpy as np


def evidence_confidence(weights: np.ndarray, confidences: np.ndarray, *, scale: float = 1.0) -> float:
    """Saturating evidence: 1 - exp(-sum(w*c)/scale), in [0,1)."""

    mass = float(np.sum(np.asarray(weights) * np.asarray(confidences)))
    return float(1.0 - np.exp(-mass / max(scale, 1e-9)))


def sign_agreement(signed: np.ndarray, weights: np.ndarray) -> float:
    """|weighted mean sign| in [0,1]: 1 = all sources agree, 0 = balanced conflict."""

    w = np.asarray(weights, dtype=float)
    if w.sum() <= 0:
        return 0.0
    return float(abs(np.sum(w * np.sign(signed))) / w.sum())
