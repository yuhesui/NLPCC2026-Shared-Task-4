"""Ablation-spec generation."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from tools.experiments.experiment_config import ExperimentConfig


def make_s1_ablation_configs(base: ExperimentConfig) -> list[ExperimentConfig]:
    params = dict(base.agent_params)
    variants: list[tuple[str, dict[str, Any]]] = [
        ("base", params),
        ("no_momentum", {**params, "momentum_weight": 0.0}),
        ("no_sector_trend", {**params, "sector_trend_weight": 0.0}),
        ("low_turnover", {**params, "rebalance_threshold": 0.05}),
    ]
    return [replace(base, name=f"{base.name}_{suffix}", agent_params=variant_params) for suffix, variant_params in variants]
