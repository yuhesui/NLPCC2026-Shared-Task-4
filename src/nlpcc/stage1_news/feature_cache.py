"""Builders for bounded Stage 1 text feature caches."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import Stage1Config


TEXT_FEATURE_MODES = (
    "no_news",
    "rule_based",
    "bge_small_zh",
    "finbert_tone_chinese",
    "hybrid_rule_bge_finbert",
)


@dataclass(frozen=True)
class TextFeatureCacheRecord:
    mode: str
    decision_date: str
    news_count: int
    cache_key: str | None
    fallback_used: bool
    event_count: int
    sentiment_count: int
    bl_view_count: int
    diagnostics: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def stage1_config_for_mode(
    mode: str,
    *,
    cache_path: Path | str | None = None,
    cache_mode: str = "read_write",
) -> dict[str, Any]:
    normalized = mode.lower()
    base: dict[str, Any] = {
        "extractor": "rule_based",
        "top_rank": 20,
        "use_llm": False,
        "text_model": {"enabled": False, "fallback": "rule_based"},
    }
    if normalized == "no_news":
        base["extractor"] = "no_llm_fallback"
    elif normalized == "rule_based":
        pass
    elif normalized == "bge_small_zh":
        base["extractor"] = "bge_small_zh"
        base["text_model"] = {
            "enabled": True,
            "model_name": "BAAI/bge-small-zh-v1.5",
            "local_path": None,
            "offline_only": True,
            "fallback": "rule_based",
        }
    elif normalized == "finbert_tone_chinese":
        base["extractor"] = "finbert_tone_chinese"
        base["text_model"] = {
            "enabled": True,
            "model_name": "yiyanghkust/finbert-tone-chinese",
            "local_path": None,
            "offline_only": True,
            "fallback": "rule_based",
        }
    elif normalized in {"hybrid", "hybrid_rule_bge_finbert", "hybrid_local_text"}:
        base["extractor"] = "hybrid_rule_bge_finbert"
        base["text_model"] = {
            "enabled": True,
            "model_name": "hybrid_rule_bge_finbert",
            "local_path": None,
            "offline_only": True,
            "fallback": "rule_based",
        }
    else:
        raise ValueError(f"Unsupported text feature mode: {mode!r}")
    if cache_path is not None:
        base["cache_path"] = str(cache_path)
        base["cache_mode"] = cache_mode
        base["cache_namespace"] = "prompt17"
        base["cache_version"] = "prompt17_stage1_v1"
    return base


def build_text_feature_cache(
    *,
    dates: tuple[str, ...],
    news_provider: Callable[[str], list[dict[str, Any]]],
    cache_path: Path,
    modes: tuple[str, ...] = TEXT_FEATURE_MODES,
    sample_limit: int | None = None,
) -> list[TextFeatureCacheRecord]:
    selected_dates = dates[: max(0, int(sample_limit))] if sample_limit is not None else dates
    records: list[TextFeatureCacheRecord] = []
    for mode in modes:
        for decision_date in selected_dates:
            news = [] if mode == "no_news" else news_provider(decision_date)
            output = run_stage1_news_pipeline(
                news,
                decision_date=decision_date,
                config=Stage1Config.from_mapping(stage1_config_for_mode(mode, cache_path=cache_path)),
            )
            records.append(
                TextFeatureCacheRecord(
                    mode=mode,
                    decision_date=decision_date,
                    news_count=len(news),
                    cache_key=output.diagnostics.get("cache_key"),
                    fallback_used=output.fallback_used,
                    event_count=len(output.events),
                    sentiment_count=len(output.sentiments),
                    bl_view_count=len(output.bl_views),
                    diagnostics=dict(output.diagnostics),
                )
            )
    return records
