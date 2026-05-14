"""Ablation helpers."""

from __future__ import annotations

from typing import Any, Mapping

from nlpcc4.common.config import deep_merge


def build_ablation_config(config: Mapping[str, Any], ablation: str) -> dict[str, Any]:
    """Return a conservative config variant for a named ablation."""
    if ablation == "no_llm":
        return deep_merge(config, {"llm": {"mode": "off"}})
    if ablation == "no_turnover_control":
        return deep_merge(config, {"execution": {"max_daily_turnover": None}})
    if ablation == "no_news_input":
        return deep_merge(config, {"data": {"same_day_news_policy": "disabled"}})
    if ablation == "strict_turnover":
        current = config.get("execution", {}).get("max_daily_turnover", 0.20)
        return deep_merge(config, {"execution": {"max_daily_turnover": max(0.01, float(current) * 0.5)}})
    return dict(config)


def run_ablation() -> None:
    """Compatibility entry point used by earlier tests."""
    return None
