"""Experiment runner for local S0/S1 research runs."""

from __future__ import annotations

import json
from typing import Any

from nlpcc.stage4_agent.models.s0_equal_weight_agent import S0EqualWeightAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from tools.backtesting.local_backtester import run_local_backtest
from tools.experiments.experiment_config import ExperimentConfig


def build_agent(agent_name: str, params: dict[str, Any] | None = None) -> Any:
    params = params or {}
    if agent_name == "s0_equal_weight":
        return S0EqualWeightAgent(**params)
    if agent_name == "s1_quant_core":
        return S1QuantCoreAgent.from_config(params)
    raise ValueError(f"Unsupported experiment agent: {agent_name!r}")


def run_experiment(config: ExperimentConfig) -> dict[str, Any]:
    output_path = config.output_dir / f"{config.name}.json"
    result = run_local_backtest(
        data_root=config.data_root,
        track=config.track,  # type: ignore[arg-type]
        agent=build_agent(config.agent_name, config.agent_params),
        output_path=output_path,
        lookback_days=config.lookback_days,
        load_news=config.load_news,
    )
    result["experiment"] = {
        "name": config.name,
        "agent_name": config.agent_name,
        "track": config.track,
        "data_root": str(config.data_root),
        "lookback_days": config.lookback_days,
        "load_news": config.load_news,
    }
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result
