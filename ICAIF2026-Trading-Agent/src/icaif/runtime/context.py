"""Context builders: turn (round, AS_OF, portfolio) into a DecisionContext.

``PanelContextBuilder`` reads a MarketPanel from a loader callable (e.g. a CSV
refreshed by an external, terms-reviewed data job) and an optional text
provider. The loader is called on every round so fresh bars are picked up;
the leakage guard still slices at AS_OF.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np

from icaif.competition.portfolio_state import PortfolioState
from icaif.competition.schedule import Round
from icaif.data.market.panel import MarketPanel
from icaif.runtime.state import DecisionContext, TextState


@dataclass
class PanelContextBuilder:
    panel_loader: Callable[[], MarketPanel]
    text_provider: Callable[[datetime], TextState] | None = None
    macro_provider: Callable[[datetime], dict[str, Any]] | None = None
    previous: dict[str, Any] | None = None

    def build(self, row: Round, as_of: datetime, portfolio: PortfolioState, phase: str) -> DecisionContext:
        view = self.panel_loader().as_of(as_of)
        px = view.last_close()
        safe_px = np.where(np.isfinite(px), px, 0.0)
        return DecisionContext(
            phase=phase, round_id=row.id, round_number=row.number, decision_time=as_of, deadline=row.deadline,
            execution_time=row.execution_time, market_state=view, portfolio_state=portfolio,
            current_weights=portfolio.weights(safe_px), nav_estimate=portfolio.nav(safe_px),
            text_state=self.text_provider(as_of) if self.text_provider else None,
            macro_state=self.macro_provider(as_of) if self.macro_provider else None,
            previous_decision=self.previous,
        )
