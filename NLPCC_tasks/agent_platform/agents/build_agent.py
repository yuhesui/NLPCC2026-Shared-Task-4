"""Official-facing submitted agent wrapper.

This file intentionally stays thin: it exposes the starter-kit-facing agent API
and delegates reusable logic to ``src/nlpcc``.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.execution.official_adapter import normalize_track, write_decision_trace  # noqa: E402
from nlpcc.runtime.system_runner import SystemRunner  # noqa: E402


class OfficialNLPCCAgent:
    """Official-compatible wrapper around the reusable SystemRunner."""

    def __init__(
        self,
        *,
        track: str = "macro",
        strategy: str | None = None,
        fallback_strategy: str | None = None,
        trace_dir: str | Path | None = None,
    ) -> None:
        self.track = normalize_track(track)
        self.strategy = strategy
        self.fallback_strategy = fallback_strategy
        self.trace_dir = Path(trace_dir) if trace_dir is not None else REPO_ROOT / "outputs" / "logs" / "decision_traces"
        self.runner = SystemRunner.for_track(
            self.track,
            strategy=strategy,
            fallback_strategy=fallback_strategy,
            trace_dir=self.trace_dir,
        )

    def decide(
        self,
        *,
        date_to_decision: str | int | None = None,
        news_data: list[dict[str, Any]] | None = None,
        historical_prices: dict[str, list[dict[str, Any]]] | None = None,
        current_portfolio: dict[str, Any] | None = None,
        market_data: dict[str, Any] | None = None,
        fund_pool: list[str] | tuple[str, ...] | None = None,
        track: str | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        decision = self.runner.run_day(
            track=track or self.track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            news=news_data,
            current_portfolio=current_portfolio,
            date_to_decision=date_to_decision,
            market_data=market_data,
        )
        final_decision = decision.as_official_decision()
        trace_path = self.trace_dir / f"{normalize_track(track or self.track)}_decision_trace.jsonl"
        write_decision_trace(
            trace_path,
            {
                "date_to_decision": date_to_decision,
                "track": normalize_track(track or self.track),
                "strategy": self.strategy,
                "fallback_strategy": self.fallback_strategy,
                "decision_trace": final_decision.get("metadata", {}).get("decision_trace"),
                "trade_count": len(final_decision.get("trades", [])),
            },
        )
        return final_decision

    async def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        """Starter-kit async API used by ``demo_backtest.py``."""

        final_decision = self.decide(**kwargs)
        await asyncio.sleep(0)
        return {"final_decision": final_decision}


def build_agent(
    *,
    track: str = "macro",
    strategy: str | None = None,
    fallback_strategy: str | None = None,
    trace_dir: str | Path | None = None,
    **_: Any,
) -> OfficialNLPCCAgent:
    return OfficialNLPCCAgent(
        track=track,
        strategy=strategy,
        fallback_strategy=fallback_strategy,
        trace_dir=trace_dir,
    )


def build_track_a_agent(**kwargs: Any) -> OfficialNLPCCAgent:
    return build_agent(track="macro", **kwargs)


def build_track_b_agent(**kwargs: Any) -> OfficialNLPCCAgent:
    return build_agent(track="sector", **kwargs)
