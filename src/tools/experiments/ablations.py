"""Ablation-spec generation for prompt10 evidence suites."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from tools.experiments.experiment_config import ExperimentConfig, ExperimentSuiteConfig


def make_s1_ablation_configs(base: ExperimentConfig) -> list[ExperimentConfig]:
    params = dict(base.agent_params)
    variants: list[tuple[str, dict[str, Any]]] = [
        ("base", params),
        ("no_momentum", {**params, "momentum_weight": 0.0}),
        ("no_sector_trend", {**params, "sector_trend_weight": 0.0}),
        ("low_turnover", {**params, "rebalance_threshold": 0.05}),
    ]
    return [replace(base, name=f"{base.name}_{suffix}", agent_params=variant_params) for suffix, variant_params in variants]


def make_prompt10_ablation_suite(
    *,
    data_root: Path = Path("data/train_2024"),
    output_dir: Path = Path("outputs/experiments/prompt10"),
    max_dates: int | None = 30,
) -> ExperimentSuiteConfig:
    common = {
        "data_root": data_root,
        "lookback_days": 60,
        "max_dates": max_dates,
        "output_dir": output_dir,
    }
    macro_constraints = {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6}
    sector_constraints = {"max_weight": 0.5, "cash_reserve": 0.03, "max_turnover": 0.6}
    experiments = [
        ExperimentConfig(
            name="s0_macro",
            agent_name="s0_equal_weight",
            track="macro",
            agent_params={"max_weight": 0.7},
            group="baseline",
            ablation="s0",
            **common,
        ),
        ExperimentConfig(
            name="s1_macro",
            agent_name="s1_quant_core",
            track="macro",
            agent_params={"track": "macro", "max_weight": 0.7},
            group="baseline",
            ablation="s1",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_macro",
            agent_name="robust_bl",
            track="macro",
            load_news=True,
            agent_params={"track": "macro", "constraints": macro_constraints},
            group="track1",
            ablation="base",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_no_news",
            agent_name="robust_bl",
            track="macro",
            load_news=False,
            agent_params={"track": "macro", "constraints": macro_constraints},
            group="track1",
            ablation="no-news",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_no_llm",
            agent_name="robust_bl",
            track="macro",
            load_news=True,
            agent_params={"track": "macro", "constraints": macro_constraints, "stage1": {"use_llm": False}},
            group="track1",
            ablation="no-LLM",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_no_text_store",
            agent_name="s1_quant_core",
            track="macro",
            load_news=False,
            agent_params={"track": "macro", "max_weight": 0.7},
            group="track1",
            ablation="no-text-store",
            notes="Uses S1 quant core as the no text-store control for the robust BL pipeline.",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_no_turnover_control",
            agent_name="robust_bl",
            track="macro",
            load_news=True,
            agent_params={
                "track": "macro",
                "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 1.0, "rebalance_threshold": 0.0},
            },
            group="track1",
            ablation="no-turnover-control",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_no_risk_control",
            agent_name="robust_bl",
            track="macro",
            load_news=True,
            agent_params={
                "track": "macro",
                "constraints": {"max_weight": 1.0, "cash_reserve": 0.0, "max_turnover": 1.0, "rebalance_threshold": 0.0},
            },
            group="track1",
            ablation="no-risk-control",
            **common,
        ),
        ExperimentConfig(
            name="robust_bl_without_confidence",
            agent_name="robust_bl",
            track="macro",
            load_news=True,
            agent_params={
                "track": "macro",
                "constraints": macro_constraints,
                "min_view_confidence": 0.0,
                "stage2": {"min_confidence": 0.0, "max_confidence": 1.0},
            },
            group="track1",
            ablation="without-confidence",
            **common,
        ),
        ExperimentConfig(
            name="sector_rotation_track2",
            agent_name="sector_rotation",
            track="sector",
            load_news=True,
            agent_params={"track": "sector", "constraints": sector_constraints},
            group="track2",
            ablation="base",
            **common,
        ),
        ExperimentConfig(
            name="sector_without_graph",
            agent_name="sector_rotation",
            track="sector",
            load_news=True,
            agent_params={"track": "sector", "constraints": sector_constraints, "use_graph": False, "graph_weight": 0.0},
            group="track2",
            ablation="sector-without-graph",
            **common,
        ),
        ExperimentConfig(
            name="sector_without_news",
            agent_name="sector_rotation",
            track="sector",
            load_news=False,
            agent_params={
                "track": "sector",
                "constraints": sector_constraints,
                "use_news": False,
                "news_weight": 0.0,
                "trend_weight": 0.85,
                "graph_weight": 0.15,
            },
            group="track2",
            ablation="sector-without-news",
            **common,
        ),
        ExperimentConfig(
            name="oco_fallback_macro",
            agent_name="oco_ensemble",
            track="macro",
            load_news=True,
            agent_params={"track": "macro", "constraints": macro_constraints},
            group="fallback",
            ablation="base",
            **common,
        ),
        ExperimentConfig(
            name="oco_without_text",
            agent_name="oco_ensemble",
            track="macro",
            load_news=False,
            agent_params={
                "track": "macro",
                "constraints": macro_constraints,
                "experts": [
                    {"name": "s1_quant_core", "prior_weight": 0.55, "config": {"track": "macro", "max_weight": 0.7}},
                    {"name": "risk_parity", "prior_weight": 0.35, "config": {"track": "macro", "constraints": macro_constraints}},
                    {"name": "conservative_ensemble", "prior_weight": 0.10, "config": {"track": "macro", "constraints": macro_constraints}},
                ],
            },
            group="fallback",
            ablation="oco-without-text",
            **common,
        ),
    ]
    return ExperimentSuiteConfig(name="prompt10_ablation_suite", experiments=tuple(experiments), report_dir=Path("outputs/reports/prompt10"))
