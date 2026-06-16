"""Prompt07 official-server replay adapter for frozen candidate target weights.

This adapter is intentionally thin. It loads precomputed target weights for a
named candidate, uses the existing production order planner to convert those
targets into official buy/sell trades, and records decision hashes for audit.
It does not change the default submitted ``build_agent.py`` runtime.
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.execution.official_adapter import (  # noqa: E402
    build_agent_input,
    normalize_track,
    write_decision_trace,
)
from nlpcc.execution.order_planner import OrderPlannerConfig, plan_orders_from_target_weights  # noqa: E402


class Prompt07OfficialReplayAgent:
    """Official API-compatible agent backed by frozen target weights."""

    def __init__(
        self,
        *,
        track: str,
        candidate_id: str,
        candidate_name: str,
        target_weights_csv: str | Path,
        trace_dir: str | Path,
        max_decision_date: int = 20251231,
    ) -> None:
        self.track = normalize_track(track)
        self.candidate_id = candidate_id
        self.candidate_name = candidate_name
        self.target_weights_csv = Path(target_weights_csv)
        self.trace_dir = Path(trace_dir)
        self.max_decision_date = int(max_decision_date)
        self.target_hash = _sha256_file(self.target_weights_csv)
        self.targets = self._load_targets(self.target_weights_csv)

    def decide(
        self,
        *,
        date_to_decision: str | int | None = None,
        historical_prices: dict[str, list[dict[str, Any]]] | None = None,
        current_portfolio: dict[str, Any] | None = None,
        news_data: list[dict[str, Any]] | None = None,
        fund_pool: list[str] | tuple[str, ...] | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        date_key = _date_key(date_to_decision)
        if int(date_key) > self.max_decision_date:
            raise ValueError(f"Prompt07 replay refuses hidden/post-2025 date {date_key}")

        pool = tuple(str(item) for item in (fund_pool or ()))
        weights = dict(self.targets.get(date_key, {}))
        if pool:
            allowed = set(pool)
            weights = {fund_id: weight for fund_id, weight in weights.items() if fund_id in allowed}

        agent_input = build_agent_input(
            track=self.track,
            fund_pool=pool,
            historical_prices=historical_prices,
            news=news_data,
            current_portfolio=current_portfolio,
        )
        order_plan = plan_orders_from_target_weights(
            weights,
            current_portfolio=agent_input["current_portfolio"],
            current_open_by_fund=agent_input["current_open_by_fund"],
            fund_pool=agent_input["fund_pool"],
            config=OrderPlannerConfig(rebalance_threshold=0.0, cash_reserve=0.0, max_weight=1.0, max_turnover=1.0),
        )

        input_hash = _stable_hash(
            {
                "date": date_key,
                "track": self.track,
                "candidate_id": self.candidate_id,
                "portfolio": current_portfolio,
                "historical_price_keys": sorted((historical_prices or {}).keys()),
                "fund_pool": list(pool),
            }
        )
        output_hash = _stable_hash({"target_weights": weights, "trades": list(order_plan.trades)})
        trace = {
            "schema_version": "prompt07_official_replay_trace_v1",
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "track": self.track,
            "date": date_key,
            "target_weights_csv": str(self.target_weights_csv),
            "target_weights_sha256": self.target_hash,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "target_weight_sum": sum(weights.values()),
            "trade_count": len(order_plan.trades),
            "rejected_trade_count": len(order_plan.rejected_trades),
            "uses_hidden_2026": False,
            "uses_online_api": False,
        }
        trace_path = self.trace_dir / f"official_server_{_track_label(self.track)}_{self.candidate_id}_decision_trace.jsonl"
        write_decision_trace(trace_path, trace)

        return {
            "target_weights": weights,
            "trades": [dict(trade) for trade in order_plan.trades],
            "reasoning": "Prompt07 official-server replay of frozen public-validation target weights.",
            "metadata": {
                **trace,
                "order_plan": order_plan.diagnostics,
                "rejected_trades": list(order_plan.rejected_trades),
                "actual_official_server_or_platform_run": True,
                "local_official_server_run": True,
                "remote_official_server_run": False,
                "official_submission_run": False,
                "proxy_run": False,
            },
        }

    async def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        final_decision = self.decide(**kwargs)
        await asyncio.sleep(0)
        return {"final_decision": final_decision}

    @staticmethod
    def _load_targets(path: Path) -> dict[str, dict[str, float]]:
        targets: dict[str, dict[str, float]] = {}
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                date_key = _date_key(row["date"])
                fund_id = str(row["fund_id"])
                targets.setdefault(date_key, {})[fund_id] = float(row["target_weight"])
        return targets


def _date_key(value: str | int | None) -> str:
    digits = "".join(char for char in str(value or "") if char.isdigit())
    if len(digits) < 8:
        raise ValueError(f"Invalid decision date: {value!r}")
    return digits[:8]


def _track_label(track: str) -> str:
    return "A" if normalize_track(track) == "macro" else "B"


def _stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
