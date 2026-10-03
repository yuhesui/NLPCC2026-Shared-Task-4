"""Simulated execution with ICAIF semantics.

* Target weights apply to pre-trade NAV ``B_k`` valued at execution prices.
* Fee = 0.1% x (buy + sell notional), deducted from cash; initial allocation
  from cash is charged.
* HOLD (no valid decision) -> no trades, no fee, holdings carry over.
* All-zero target -> full liquidation to cash (fee on the sells).
* If a target would leave negative cash after the fee, buys are scaled down
  until cash >= 0 and the adjustment is reported (organizer behaviour on this
  edge case is undocumented; see open question Q3).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.competition.portfolio_state import PortfolioState
from icaif.core.constants import FEE_RATE


@dataclass(frozen=True)
class Fill:
    state: PortfolioState
    nav_before: float
    traded_notional: float
    fee: float
    funding_scale: float  # 1.0 unless buys were scaled to fund the fee


def execute_target(state: PortfolioState, target: np.ndarray, prices: np.ndarray, *, fee_rate: float = FEE_RATE) -> Fill:
    prices = np.asarray(prices, dtype=float)
    if not (np.isfinite(prices).all() and (prices > 0).all()):
        raise ValueError("execution prices must be positive and finite for all 30 symbols")
    shares0 = np.asarray(state.shares, dtype=float)
    nav = state.nav(prices)
    target = np.asarray(target, dtype=float)

    def trade(scale: float) -> tuple[np.ndarray, float, float, float]:
        w = target * scale
        shares1 = w * nav / prices
        notional = float(np.abs(shares1 - shares0) @ prices)
        fee = fee_rate * notional
        cash = nav - float(shares1 @ prices) - fee
        return shares1, notional, fee, cash

    scale = 1.0
    shares1, notional, fee, cash = trade(scale)
    if cash < -1e-9 * nav:
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if trade(mid)[3] >= 0:
                lo = mid
            else:
                hi = mid
        scale = lo
        shares1, notional, fee, cash = trade(scale)
    new_state = PortfolioState(cash=max(cash, 0.0) if cash > -1e-6 else cash, shares=tuple(float(x) for x in shares1),
                               source="simulated")
    return Fill(new_state, nav, notional, fee, scale)
