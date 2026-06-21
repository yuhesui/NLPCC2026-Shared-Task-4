"""Official-facing submitted agent wrapper.

This file intentionally stays thin: it exposes the starter-kit-facing agent API
and delegates to the vendored submission runtime under ``NLPCC_tasks/nlpcc``.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) in sys.path:
    sys.path.remove(str(PACKAGE_ROOT))
sys.path.insert(0, str(PACKAGE_ROOT))

from nlpcc.execution.official_adapter import normalize_track, write_decision_trace  # noqa: E402


class OfficialNLPCCAgent:
    """Official-compatible wrapper around the fixed submission candidate."""

    def __init__(
        self,
        *,
        track: str = "macro",
        strategy: str | None = None,
        fallback_strategy: str | None = None,
        config_root: str | Path | None = None,
        trace_dir: str | Path | None = None,
    ) -> None:
        self.track = normalize_track(track)
        env_strategy_key = "NLPCC_TRACK_B_STRATEGY" if self.track == "sector" else "NLPCC_TRACK_A_STRATEGY"
        env_fallback_key = "NLPCC_TRACK_B_FALLBACK" if self.track == "sector" else "NLPCC_TRACK_A_FALLBACK"
        env_config_root = os.environ.get("NLPCC_CONFIG_ROOT")
        del env_config_root, config_root, env_fallback_key
        self.strategy = strategy or os.environ.get(env_strategy_key) or "phase12_final"
        self.fallback_strategy = fallback_strategy
        self.trace_dir = Path(trace_dir) if trace_dir is not None else PACKAGE_ROOT / "runtime_logs" / "decision_traces"
        if not _is_phase12_final_requested(self.strategy):
            raise ValueError("submission_package_supports_phase12_final_only")
        agent_dir = Path(__file__).resolve().parent
        if str(agent_dir) not in sys.path:
            sys.path.insert(0, str(agent_dir))
        from phase12_final_agent import build_phase12_final_agent  # noqa: WPS433

        self.delegate = build_phase12_final_agent(track=self.track, trace_dir=self.trace_dir)

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
        del market_data
        final_decision = self.delegate.decide(
            track=track or self.track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            news_data=news_data,
            current_portfolio=current_portfolio,
            date_to_decision=date_to_decision,
        )
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
    config_root: str | Path | None = None,
    trace_dir: str | Path | None = None,
    **_: Any,
) -> Any:
    requested_strategy = strategy or os.environ.get("NLPCC_TRACK_B_STRATEGY" if normalize_track(track) == "sector" else "NLPCC_TRACK_A_STRATEGY") or "phase12_final"
    if _is_phase12_final_requested(requested_strategy):
        agent_dir = Path(__file__).resolve().parent
        if str(agent_dir) not in sys.path:
            sys.path.insert(0, str(agent_dir))
        from phase12_final_agent import build_phase12_final_agent  # noqa: WPS433

        return build_phase12_final_agent(track=track, trace_dir=trace_dir)
    return OfficialNLPCCAgent(
        track=track,
        strategy=strategy,
        fallback_strategy=fallback_strategy,
        config_root=config_root,
        trace_dir=trace_dir,
    )


def _is_phase12_final_requested(strategy: str | None) -> bool:
    return str(os.environ.get("NLPCC_PHASE12_FINAL", "")).lower() in {"1", "true", "yes"} or str(strategy or "").lower() in {
        "phase12_final",
        "phase12_final_a2",
        "phase12_final_b2",
        "prompt04_phase12_final",
    }


def build_track_a_agent(**kwargs: Any) -> Any:
    return build_agent(track="macro", **kwargs)


def build_track_b_agent(**kwargs: Any) -> Any:
    return build_agent(track="sector", **kwargs)
