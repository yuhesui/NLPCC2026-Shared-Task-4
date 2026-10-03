"""Explicit deterministic fallback chain.

Adapted from AlphaAllocator ``runtime/fallback_manager.py`` (primary ->
validate -> fallback, every switch recorded). Differences:

* the chain is ordered and configurable: primary pipeline -> fallback
  pipeline(s) -> terminal action;
* only *anticipated* failure classes trigger a fallback (data, history,
  model availability, numeric/validation failures). Unexpected exception
  types are still caught at the round boundary — one round must not kill the
  live process — but are recorded as ``unexpected_exception`` with the type
  name, raise an alert flag, and are re-raised in ``strict`` mode (tests and
  research runs use strict mode so bugs surface).
* the terminal action is HOLD (no submission: the platform keeps current
  holdings with no fee), never "invent a portfolio".
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from icaif.competition.portfolio_state import PortfolioStateIncomplete
from icaif.core.leakage_guard import LeakageViolation
from icaif.data.market.loaders import SourceUnavailable
from icaif.portfolio.constraints import ZeroSignalError
from icaif.portfolio.pipeline import InsufficientHistory
from icaif.portfolio.target_weights import InvalidTargetError

ANTICIPATED = (
    InsufficientHistory,
    SourceUnavailable,
    PortfolioStateIncomplete,
    InvalidTargetError,
    ZeroSignalError,
    np.linalg.LinAlgError,
    FloatingPointError,
)
# Leakage is never "fallen back" from silently: it is a bug. It is caught only
# so the round can HOLD in live mode, and always flagged as critical.
CRITICAL = (LeakageViolation,)


@dataclass(frozen=True)
class FallbackPolicy:
    chain: tuple[str, ...]  # pipeline names in order, first = primary
    strict: bool = False  # re-raise unexpected exceptions (tests/research)
    terminal_action: str = "HOLD"


def classify_exception(error: BaseException) -> str:
    if isinstance(error, CRITICAL):
        return "critical_leakage"
    if isinstance(error, ANTICIPATED):
        return "anticipated:" + type(error).__name__
    return "unexpected_exception:" + type(error).__name__
