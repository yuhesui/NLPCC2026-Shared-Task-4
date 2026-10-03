"""Cross-sectional transforms over the 30-asset vector (NaN-aware)."""

from __future__ import annotations

import numpy as np

from icaif.core.universe import SECTOR_OF, SYMBOLS


def winsorize(x: np.ndarray, z: float = 3.0) -> np.ndarray:
    mu, sd = np.nanmean(x), np.nanstd(x)
    if not np.isfinite(sd) or sd == 0:
        return x.copy()
    return np.clip(x, mu - z * sd, mu + z * sd)


def zscore(x: np.ndarray, clip: float | None = 3.0) -> np.ndarray:
    """Cross-sectional z-score; NaN stays NaN; zero dispersion -> zeros."""

    finite = np.isfinite(x)
    out = np.full_like(x, np.nan, dtype=float)
    if finite.sum() < 2:
        out[finite] = 0.0
        return out
    mu = x[finite].mean()
    sd = x[finite].std()
    out[finite] = 0.0 if sd == 0 else (x[finite] - mu) / sd
    if clip is not None:
        out = np.clip(out, -clip, clip)
    return out


def rank_score(x: np.ndarray) -> np.ndarray:
    """Ranks mapped to [-1, 1] (ties averaged); NaN stays NaN."""

    finite = np.flatnonzero(np.isfinite(x))
    out = np.full(x.shape, np.nan)
    if finite.size == 0:
        return out
    if finite.size == 1:
        out[finite] = 0.0
        return out
    values = x[finite]
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(finite.size)
    ranks[order] = np.arange(finite.size, dtype=float)
    for v in np.unique(values):  # average ties
        tie = values == v
        ranks[tie] = ranks[tie].mean()
    out[finite] = 2.0 * ranks / (finite.size - 1) - 1.0
    return out


def sector_demean(x: np.ndarray) -> np.ndarray:
    out = x.astype(float).copy()
    sectors = np.array([SECTOR_OF[s] for s in SYMBOLS])
    for sector in np.unique(sectors):
        idx = (sectors == sector) & np.isfinite(out)
        if idx.any():
            out[idx] -= out[idx].mean()
    return out


def nan_to_neutral(x: np.ndarray, neutral: float = 0.0) -> np.ndarray:
    return np.where(np.isfinite(x), x, neutral)
