"""Round-aware decision context and persistent agent state.

``DecisionContext`` is everything one round's decision may read. It is built
by the backtest engine or the live runner *after* freezing ``decision_time``
(AS_OF); all market/text inputs inside it are already point-in-time views.

``AgentState`` persists across rounds and restarts (JSON checkpoint written
atomically): NAV peak (for drawdown-based exposure), daily turnover budget,
held-name set (selection hysteresis), last decision.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from icaif.competition.portfolio_state import PortfolioState
from icaif.data.market.panel import MarketView


@dataclass(frozen=True)
class TextState:
    """Per-asset text signals at decision time (NaN = no information).

    Produced by ``icaif.nlp.feature_store.build_text_state``; ablations
    (``icaif.experiments.ablations``) transform this object, never the raw data.
    """

    score: np.ndarray  # signed directional score
    confidence: np.ndarray  # [0,1]
    relevance: np.ndarray  # [0,1]
    event_multiplier: np.ndarray  # >= 0, from event-type priors
    article_count: np.ndarray
    novelty: np.ndarray
    evidence: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    sources_failed: tuple[str, ...] = ()
    model_ids: tuple[str, ...] = ()

    @classmethod
    def empty(cls, n: int) -> TextState:
        nan = np.full(n, np.nan)
        zeros = np.zeros(n)
        return cls(nan, zeros.copy(), zeros.copy(), np.ones(n), zeros.copy(), zeros.copy())

    def summary(self) -> dict[str, Any]:
        info = np.isfinite(self.score)
        return {
            "assets_with_signal": int(info.sum()),
            "articles": int(np.nansum(self.article_count)),
            "mean_abs_score": float(np.nanmean(np.abs(self.score))) if info.any() else 0.0,
            "sources_failed": list(self.sources_failed),
            "model_ids": list(self.model_ids),
        }


@dataclass(frozen=True)
class DecisionContext:
    phase: str
    round_id: str
    round_number: int
    decision_time: datetime  # frozen AS_OF
    deadline: datetime
    execution_time: datetime
    market_state: MarketView
    portfolio_state: PortfolioState
    current_weights: np.ndarray  # drifted weights at latest visible prices
    nav_estimate: float
    text_state: TextState | None = None
    macro_state: dict[str, Any] | None = None
    previous_decision: dict[str, Any] | None = None

    @property
    def trading_day(self) -> date:
        from icaif.core.time import et_date

        return et_date(self.execution_time)


@dataclass
class AgentState:
    nav_peak: float = 0.0
    held: list[bool] = field(default_factory=list)
    budget_day: str | None = None
    budget_used: float = 0.0
    last_round_id: str | None = None
    last_target: list[float] | None = None
    rounds_decided: int = 0
    rounds_rebalanced: int = 0
    fallbacks_used: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def nav_drawdown(self, nav: float) -> float:
        self.nav_peak = max(self.nav_peak, nav)
        return 0.0 if self.nav_peak <= 0 else max(0.0, 1.0 - nav / self.nav_peak)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".state", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(asdict(self), stream, indent=2, sort_keys=True)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path: Path) -> AgentState:
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)
