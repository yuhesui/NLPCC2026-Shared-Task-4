"""Experiment runner for local ablations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nlpcc.stage4_agent.models.conservative_ensemble_agent import ConservativeEnsembleAgent
from nlpcc.stage4_agent.models.kg_moe_lite_agent import KGMoELiteAgent
from nlpcc.stage4_agent.models.oco_ensemble_agent import OCOEnsembleAgent
from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent
from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent
from nlpcc.stage4_agent.models.s0_equal_weight_agent import S0EqualWeightAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from nlpcc.stage4_agent.models.sector_rotation_agent import SectorRotationAgent
from tools.backtesting.local_backtester import run_local_backtest
from tools.experiments.experiment_config import ExperimentConfig, ExperimentSuiteConfig
from tools.experiments.result_store import ResultStore


def build_agent(agent_name: str, params: dict[str, Any] | None = None) -> Any:
    params = params or {}
    if agent_name == "s0_equal_weight":
        return S0EqualWeightAgent(**params)
    if agent_name == "s1_quant_core":
        return S1QuantCoreAgent.from_config(params)
    if agent_name == "risk_parity":
        return RiskParityAgent.from_config(params)
    if agent_name == "robust_bl":
        return RobustBLAgent.from_config(params)
    if agent_name == "sector_rotation":
        return SectorRotationAgent.from_config(params)
    if agent_name == "kg_moe_lite":
        return KGMoELiteAgent.from_config(params)
    if agent_name == "conservative_ensemble":
        return ConservativeEnsembleAgent.from_config(params)
    if agent_name == "oco_ensemble":
        return OCOEnsembleAgent.from_config(params)
    raise ValueError(f"Unsupported experiment agent: {agent_name!r}")


def run_experiment(config: ExperimentConfig) -> dict[str, Any]:
    output_path = config.output_dir / f"{config.run_id}.json"
    result = run_local_backtest(
        data_root=config.data_root,
        track=config.track,  # type: ignore[arg-type]
        agent=build_agent(config.agent_name, config.agent_params),
        output_path=output_path,
        lookback_days=config.lookback_days,
        load_news=config.load_news,
        initial_capital=config.initial_capital,
        news_lookback_calendar_days=config.news_lookback_calendar_days,
        max_dates=config.max_dates,
    )
    result["experiment"] = {
        "name": config.name,
        "run_id": config.run_id,
        "config_hash": config.config_hash(),
        "agent_name": config.agent_name,
        "track": config.track,
        "data_root": str(config.data_root),
        "lookback_days": config.lookback_days,
        "max_dates": config.max_dates,
        "load_news": config.load_news,
        "news_lookback_calendar_days": config.news_lookback_calendar_days,
        "ablation": config.ablation,
        "group": config.group,
        "notes": config.notes,
        "agent_params": config.agent_params,
    }
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def run_suite(suite: ExperimentSuiteConfig, *, output_dir: Path | None = None) -> list[dict[str, Any]]:
    root = output_dir or (suite.experiments[0].output_dir if suite.experiments else Path("outputs/experiments"))
    store = ResultStore(root)
    results: list[dict[str, Any]] = []
    for config in suite.experiments:
        resolved = config if output_dir is None else ExperimentConfig.from_mapping({**config.to_mapping(), "output_dir": root})
        result = run_experiment(resolved)
        store.write(resolved.run_id, result)
        results.append(result)
    return results
