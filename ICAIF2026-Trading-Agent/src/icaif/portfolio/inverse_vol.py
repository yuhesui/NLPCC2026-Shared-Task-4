"""Inverse-volatility weights (ported from AlphaAllocator, gross made explicit)."""

from __future__ import annotations

import numpy as np

from icaif.portfolio.constraints import Constraints, scale_to_capped_simplex


def inverse_vol_weights(vol: np.ndarray, gross: float, cons: Constraints | None = None) -> np.ndarray:
    """w_i ∝ 1/σ_i, capped, summing to ``gross``. Assets with unknown vol get 0."""

    cons = cons or Constraints()
    vol = np.asarray(vol, dtype=float)
    inv = np.where(np.isfinite(vol) & (vol > 0), 1.0 / np.where(vol > 0, vol, 1.0), 0.0)
    return scale_to_capped_simplex(inv, cons.max_weight, gross, on_zero="cash")
