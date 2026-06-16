"""Prompt09 official-facing real-transformer news overlay agent.

This adapter recomputes the news tensor from the daily visible news payload.
It refuses proxy mode and fixed target replay; it is not the default submitted
runtime unless explicitly selected by a Prompt09 runner.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.execution.official_adapter import build_agent_input, normalize_track, write_decision_trace  # noqa: E402
from nlpcc.execution.order_planner import OrderPlannerConfig, plan_orders_from_target_weights  # noqa: E402
from nlpcc.news_overlay.production_tensor import (  # noqa: E402
    ProductionRealNLPError,
    RealTransformerNewsTensorConfig,
    RealTransformerNewsTensorProvider,
    enforce_production_no_proxy_policy,
    stable_hash,
)
from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent  # noqa: E402
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent  # noqa: E402


PROMPT09_CANDIDATES: dict[str, dict[str, Any]] = {
    "A0": {
        "track": "macro",
        "candidate": "G00A",
        "method_stack": "N0/I0/S0",
        "uses_news_overlay": False,
        "base_agent": "risk_parity",
    },
    "A2_real": {
        "track": "macro",
        "candidate": "G11A",
        "method_stack": "N13/I6/S13",
        "uses_news_overlay": True,
        "base_agent": "risk_parity",
        "overlay_cap": 0.010,
        "turnover_cap": 0.035,
        "confidence_gate": 0.35,
        "deadband": 0.00008,
    },
    "A1_real": {
        "track": "macro",
        "candidate": "G12A",
        "method_stack": "N2345/I256/S13",
        "uses_news_overlay": True,
        "base_agent": "risk_parity",
        "overlay_cap": 0.008,
        "turnover_cap": 0.030,
        "confidence_gate": 0.38,
        "deadband": 0.00008,
    },
    "B0": {
        "track": "sector",
        "candidate": "G00B",
        "method_stack": "N0/I0/S0",
        "uses_news_overlay": False,
        "base_agent": "s1_quant_core",
    },
    "B2_real": {
        "track": "sector",
        "candidate": "G15B",
        "method_stack": "N4/I6/S2",
        "uses_news_overlay": True,
        "base_agent": "s1_quant_core",
        "overlay_cap": 0.012,
        "turnover_cap": 0.035,
        "confidence_gate": 0.35,
        "deadband": 0.00008,
    },
    "B3_real": {
        "track": "sector",
        "candidate": "G21B",
        "method_stack": "N2345/I256/S5",
        "uses_news_overlay": True,
        "base_agent": "s1_quant_core",
        "overlay_cap": 0.008,
        "turnover_cap": 0.030,
        "confidence_gate": 0.38,
        "deadband": 0.00008,
    },
}


class Prompt09RealTransformerAgent:
    """Official API-compatible real-transformer overlay agent."""

    def __init__(
        self,
        *,
        track: str,
        candidate_id: str,
        trace_dir: str | Path,
        candidate_config: Mapping[str, Any] | None = None,
        max_decision_date: int = 20251231,
        ablation_type: str = "active_real_tensor",
    ) -> None:
        self.track = normalize_track(track)
        self.candidate_id = str(candidate_id)
        base = dict(PROMPT09_CANDIDATES.get(self.candidate_id, {}))
        if not base:
            raise KeyError(f"unknown_prompt09_candidate:{candidate_id}")
        base.update(dict(candidate_config or {}))
        if normalize_track(str(base.get("track", self.track))) != self.track:
            raise ValueError(f"Candidate {candidate_id} is not compatible with track {track}")
        self.candidate_config = base
        self.trace_dir = Path(trace_dir)
        self.max_decision_date = int(max_decision_date)
        self.ablation_type = ablation_type
        self.previous_weights: dict[str, float] | None = None
        self.provider: RealTransformerNewsTensorProvider | None = None
        if self.candidate_config.get("uses_news_overlay"):
            tensor_config = RealTransformerNewsTensorConfig.from_mapping(
                {
                    "candidate_id": self.candidate_id,
                    "method_stack": self.candidate_config["method_stack"],
                    "required_model_roles": self.candidate_config.get(
                        "required_model_roles",
                        ("embedding_encoder", "financial_sentiment"),
                    ),
                    "overlay_cap": self.candidate_config.get("overlay_cap", 0.012),
                    "turnover_cap": self.candidate_config.get("turnover_cap", 0.035),
                    "confidence_gate": self.candidate_config.get("confidence_gate", 0.35),
                    "deadband": self.candidate_config.get("deadband", 0.00008),
                    "device": self.candidate_config.get("device", "auto"),
                    "batch_size": self.candidate_config.get("batch_size", 16),
                    "max_news_per_day": self.candidate_config.get("max_news_per_day", 8),
                    "production_real_nlp": self.candidate_config.get("production_real_nlp", True),
                    "allow_proxy_news": self.candidate_config.get("allow_proxy_news", False),
                    "allow_heuristic_news": self.candidate_config.get("allow_heuristic_news", False),
                    "allow_fixed_target_replay": self.candidate_config.get("allow_fixed_target_replay", False),
                    "allow_old_research_table_replay": self.candidate_config.get("allow_old_research_table_replay", False),
                    "local_files_only": self.candidate_config.get("local_files_only", True),
                }
            )
            enforce_production_no_proxy_policy(tensor_config)
            self.provider = RealTransformerNewsTensorProvider(tensor_config)

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
            raise ValueError(f"Prompt09 refuses hidden/post-2025 date {date_key}")
        agent_input = build_agent_input(
            track=self.track,
            fund_pool=fund_pool,
            historical_prices=historical_prices,
            news=news_data,
            current_portfolio=current_portfolio,
        )
        base_decision = self._base_decision(agent_input)
        base_weights = {
            str(fund): float(weight)
            for fund, weight in (base_decision.get("target_weights") or {}).items()
            if str(fund) in set(agent_input["fund_pool"])
        }
        tensor_hash = ""
        model_hash = ""
        news_tensor_rows: list[dict[str, Any]] = []
        blocked_reason = ""
        real_transformer_executed = False
        overlay_diag: dict[str, Any] = {
            "mean_abs_overlay": 0.0,
            "overlay_nonzero": False,
            "ablation_type": self.ablation_type,
        }
        target_weights = dict(base_weights)

        if self.candidate_config.get("uses_news_overlay"):
            if self.provider is None:
                raise ProductionRealNLPError("blocked_missing_local_model", "Prompt09 provider not initialized")
            tensor = self.provider.build(
                date_key,
                list(news_data or []),
                self.track,
                {**self.candidate_config, "fund_pool": agent_input["fund_pool"]},
            )
            tensor_hash = tensor.tensor_hash
            model_hash = stable_hash(list(tensor.model_status_rows))
            news_tensor_rows = tensor.rows.to_dict("records")
            real_transformer_executed = tensor.manifest.get("real_transformer_executed") == "true"
            target_weights, overlay_diag = self.provider.apply_overlay(
                base_weights,
                tensor.rows,
                previous_weights=self.previous_weights,
                ablation_type=self.ablation_type,
            )
        self.previous_weights = dict(target_weights)

        order_plan = plan_orders_from_target_weights(
            target_weights,
            current_portfolio=agent_input["current_portfolio"],
            current_open_by_fund=agent_input["current_open_by_fund"],
            fund_pool=agent_input["fund_pool"],
            config=OrderPlannerConfig(rebalance_threshold=0.0, cash_reserve=0.0, max_weight=1.0, max_turnover=1.0),
        )
        output_weight_hash = _stable_hash({"target_weights": target_weights, "trades": list(order_plan.trades)})
        trace = {
            "schema_version": "prompt09_real_transformer_trace_v1",
            "candidate_id": self.candidate_id,
            "candidate": self.candidate_config.get("candidate"),
            "method_stack": self.candidate_config.get("method_stack"),
            "track": self.track,
            "date": date_key,
            "production_real_nlp": True,
            "real_transformer_executed": real_transformer_executed,
            "proxy_mode": False,
            "heuristic_fallback_used": False,
            "fixed_target_replay_used": False,
            "network_attempted": False,
            "local_files_only": True,
            "model_hash": model_hash,
            "news_tensor_hash": tensor_hash,
            "news_tensor_row_count": len(news_tensor_rows),
            "output_weight_hash": output_weight_hash,
            "mean_abs_overlay": overlay_diag.get("mean_abs_overlay", 0.0),
            "overlay_nonzero": overlay_diag.get("overlay_nonzero", False),
            "blocked_reason": blocked_reason,
            "uses_hidden_2026": False,
            "uses_online_api": False,
        }
        trace_path = self.trace_dir / f"official_server_{_track_label(self.track)}_{self.candidate_id}_decision_trace.jsonl"
        write_decision_trace(trace_path, trace)
        return {
            "target_weights": target_weights,
            "trades": [dict(trade) for trade in order_plan.trades],
            "reasoning": "Prompt09 real local transformer news tensor overlay." if real_transformer_executed else "Prompt09 no-news base.",
            "metadata": {
                **trace,
                "agent": "Prompt09RealTransformerAgent",
                "base_agent": self.candidate_config.get("base_agent"),
                "order_plan": order_plan.diagnostics,
                "news_tensor_sample_rows": news_tensor_rows[:3],
                "actual_official_server_or_platform_run": True,
                "local_official_server_run": False,
                "local_official_platform_run": True,
                "remote_official_server_run": False,
                "official_submission_run": False,
                "proxy_run": False,
                "rejected_trades": list(order_plan.rejected_trades),
            },
        }

    async def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        final_decision = self.decide(**kwargs)
        await asyncio.sleep(0)
        return {"final_decision": final_decision}

    def _base_decision(self, agent_input: Mapping[str, Any]) -> dict[str, Any]:
        if self.candidate_config.get("base_agent") == "risk_parity":
            return RiskParityAgent.from_config({"track": self.track}).make_decision(
                track=self.track,
                fund_pool=agent_input["fund_pool"],
                historical_prices=agent_input["historical_prices"],
                current_portfolio=agent_input["current_portfolio"],
            )
        return S1QuantCoreAgent.from_config({"track": self.track}).make_decision(
            track=self.track,
            fund_pool=agent_input["fund_pool"],
            historical_prices=agent_input["historical_prices"],
            current_portfolio=agent_input["current_portfolio"],
        )


def build_prompt09_agent(
    *,
    track: str,
    candidate_id: str,
    trace_dir: str | Path,
    candidate_config: Mapping[str, Any] | None = None,
    ablation_type: str = "active_real_tensor",
    **_: Any,
) -> Prompt09RealTransformerAgent:
    return Prompt09RealTransformerAgent(
        track=track,
        candidate_id=candidate_id,
        trace_dir=trace_dir,
        candidate_config=candidate_config,
        ablation_type=ablation_type,
    )


def _date_key(value: str | int | None) -> str:
    digits = "".join(char for char in str(value or "") if char.isdigit())
    if len(digits) < 8:
        raise ValueError(f"Invalid decision date: {value!r}")
    return digits[:8]


def _track_label(track: str) -> str:
    return "A" if normalize_track(track) == "macro" else "B"


def _stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()

