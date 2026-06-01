"""Stage 1 news-processing orchestration."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from dataclasses import replace

from nlpcc.stage1_news.models.no_llm_fallback import no_llm_fallback_output
from nlpcc.stage1_news.models.bge_small_zh_extractor import BgeSmallZhEmbeddingExtractor, DEFAULT_BGE_MODEL
from nlpcc.stage1_news.models.finbert_tone_chinese_extractor import (
    DEFAULT_FINBERT_MODEL,
    FinbertToneChineseSentimentExtractor,
)
from nlpcc.stage1_news.models.hybrid_local_text_extractor import HybridLocalTextExtractor
from nlpcc.stage1_news.models.rule_based_extractor import RuleBasedNewsExtractor
from nlpcc.stage1_news.schema import NormalizedNewsItem, Stage1Config, Stage1Output
from nlpcc.stage1_news.text_model_config import TextModelConfig
from nlpcc.stage1_news.validators import assert_valid_stage1_output


OFFICIAL_NEWS_CUTOFF = time(15, 0)


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text[:19] if "%H" in fmt else text[:10], fmt)
        except ValueError:
            continue
    return None


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    parsed = _parse_datetime(value)
    return parsed.date() if parsed else None


def _decision_date(value: int | str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value)
    return datetime.strptime(text.replace("-", "")[:8], "%Y%m%d").date()


def normalize_news_items(raw_news: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> tuple[NormalizedNewsItem, ...]:
    items: list[NormalizedNewsItem] = []
    for index, row in enumerate(raw_news):
        title = str(row.get("title", row.get("TITLE", "")) or "").strip()
        content = str(row.get("content", row.get("CONTENT", "")) or "").strip()
        source = str(row.get("source", row.get("SOURCE", row.get("NEWS_SOURCE", "unknown"))) or "unknown")
        ranking_raw = row.get("ranking", row.get("RANKING"))
        try:
            ranking = int(ranking_raw) if ranking_raw not in (None, "") else None
        except ValueError:
            ranking = None
        publish_time = _parse_datetime(row.get("publish_time", row.get("PUBLISH_TIME")))
        trade_date = _parse_date(row.get("trade_date", row.get("THEDATE", row.get("date"))))
        news_id = str(
            row.get(
                "news_id",
                row.get("content_id", row.get("ID", f"{source}:{trade_date or 'nodate'}:{ranking or index}")),
            )
        )
        items.append(
            NormalizedNewsItem(
                news_id=news_id,
                source=source,
                title=title,
                content=content,
                ranking=ranking,
                publish_time=publish_time,
                trade_date=trade_date,
                raw=dict(row),
            )
        )
    return tuple(items)


def filter_visible_news(
    items: tuple[NormalizedNewsItem, ...],
    *,
    decision_date: int | str | date | datetime | None = None,
    top_rank: int = 20,
    cutoff: time = OFFICIAL_NEWS_CUTOFF,
) -> tuple[tuple[NormalizedNewsItem, ...], dict[str, int]]:
    resolved_date = _decision_date(decision_date)
    visible: list[NormalizedNewsItem] = []
    filtered_future = 0
    filtered_cutoff = 0
    filtered_rank = 0
    filtered_empty = 0
    for item in items:
        if not item.text:
            filtered_empty += 1
            continue
        if item.ranking is not None and item.ranking > top_rank:
            filtered_rank += 1
            continue
        publish_date = item.publish_time.date() if item.publish_time else item.trade_date
        if resolved_date and publish_date and publish_date > resolved_date:
            filtered_future += 1
            continue
        if resolved_date and item.publish_time and item.publish_time.date() == resolved_date and item.publish_time.time() >= cutoff:
            filtered_cutoff += 1
            continue
        visible.append(item)
    visible.sort(key=lambda item: (item.ranking if item.ranking is not None else 999, item.news_id))
    return tuple(visible), {
        "filtered_future": filtered_future,
        "filtered_after_cutoff": filtered_cutoff,
        "filtered_rank": filtered_rank,
        "filtered_empty": filtered_empty,
    }


def run_stage1_news_pipeline(
    raw_news: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
    *,
    decision_date: int | str | date | datetime | None = None,
    config: Stage1Config | dict[str, Any] | None = None,
) -> Stage1Output:
    cfg = config if isinstance(config, Stage1Config) else Stage1Config.from_mapping(config)
    cache_store = None
    cache_key = None
    if cfg.cache_path and cfg.cache_mode in {"read", "read_write", "write"}:
        from nlpcc.stage1_news.text_feature_store import TextFeatureStore

        cache_store = TextFeatureStore(cfg.cache_path)
        cache_key = cache_store.key_for(raw_news or (), decision_date=decision_date, config=cfg)
        if cfg.cache_mode in {"read", "read_write"}:
            cached = cache_store.read(cache_key)
            if cached is not None:
                cached.diagnostics["cache_hit"] = True
                cached.diagnostics["cache_key"] = cache_key
                return cached
    if not raw_news:
        output = no_llm_fallback_output("missing_news", cfg)
        assert_valid_stage1_output(output)
        if cache_store is not None and cache_key is not None and cfg.cache_mode in {"write", "read_write"}:
            output.diagnostics["cache_hit"] = False
            output.diagnostics["cache_key"] = cache_key
            cache_store.write(cache_key, output, metadata={"decision_date": str(decision_date), "extractor": cfg.extractor})
        return output

    normalized = normalize_news_items(tuple(raw_news))
    visible, diagnostics = filter_visible_news(normalized, decision_date=decision_date, top_rank=cfg.top_rank)
    if not visible:
        output = no_llm_fallback_output("no_visible_valid_news", cfg)
        output.diagnostics.update(diagnostics)
        assert_valid_stage1_output(output)
        if cache_store is not None and cache_key is not None and cfg.cache_mode in {"write", "read_write"}:
            output.diagnostics["cache_hit"] = False
            output.diagnostics["cache_key"] = cache_key
            cache_store.write(cache_key, output, metadata={"decision_date": str(decision_date), "extractor": cfg.extractor})
        return output
    output = _extract_visible_news(visible, cfg)
    output.diagnostics.update(diagnostics)
    assert_valid_stage1_output(output)
    if cache_store is not None and cache_key is not None and cfg.cache_mode in {"write", "read_write"}:
        output.diagnostics["cache_hit"] = False
        output.diagnostics["cache_key"] = cache_key
        cache_store.write(cache_key, output, metadata={"decision_date": str(decision_date), "extractor": cfg.extractor})
    return output


def _extract_visible_news(visible: tuple[NormalizedNewsItem, ...], cfg: Stage1Config) -> Stage1Output:
    extractor = (cfg.extractor or "rule_based").lower()
    if cfg.text_model.enabled and extractor == "rule_based":
        model_name = (cfg.text_model.model_name or "").lower()
        if "finbert" in model_name:
            extractor = "finbert_tone_chinese"
        elif "bge" in model_name:
            extractor = "bge_small_zh"
        else:
            extractor = "hybrid_rule_bge_finbert"

    if extractor == "no_llm_fallback":
        return no_llm_fallback_output("configured_no_llm_fallback", cfg)
    if extractor == "rule_based":
        return RuleBasedNewsExtractor(cfg).extract(visible)
    if extractor in {"finbert", "finbert_tone_chinese"}:
        return _finbert_output(visible, cfg)
    if extractor in {"bge", "bge_small_zh"}:
        return _bge_output(visible, cfg)
    if extractor in {"hybrid", "hybrid_rule_bge_finbert", "hybrid_local_text"}:
        return HybridLocalTextExtractor(cfg).extract(visible)
    fallback = RuleBasedNewsExtractor(cfg).extract(visible)
    fallback.diagnostics["unknown_extractor_fallback"] = extractor
    return fallback


def _finbert_output(visible: tuple[NormalizedNewsItem, ...], cfg: Stage1Config) -> Stage1Output:
    rule_output = RuleBasedNewsExtractor(cfg).extract(visible)
    text_cfg = _model_config(cfg, DEFAULT_FINBERT_MODEL)
    sentiments = FinbertToneChineseSentimentExtractor(text_cfg).classify_items(visible)
    diagnostics = dict(rule_output.diagnostics)
    diagnostics.update(
        {
            "model": "finbert_tone_chinese",
            "sentiment_model": text_cfg.model_name,
            "local_text_fallback_used": any(bool(item.model_metadata.get("fallback_used")) for item in sentiments),
        }
    )
    return Stage1Output(
        items=rule_output.items,
        sentiments=sentiments,
        events=rule_output.events,
        sector_impacts=rule_output.sector_impacts,
        bl_views=rule_output.bl_views,
        fallback_used=rule_output.fallback_used,
        diagnostics=diagnostics,
    )


def _bge_output(visible: tuple[NormalizedNewsItem, ...], cfg: Stage1Config) -> Stage1Output:
    rule_output = RuleBasedNewsExtractor(cfg).extract(visible)
    text_cfg = _model_config(cfg, DEFAULT_BGE_MODEL)
    embeddings = BgeSmallZhEmbeddingExtractor(text_cfg).embed_items(visible)
    by_news = {signal.news_id: signal for signal in embeddings}
    events = tuple(
        replace(
            event,
            relevance_score=round(float(by_news[event.news_id].relevance_score), 6) if event.news_id in by_news else 0.0,
            embedding_ref=by_news[event.news_id].embedding_ref if event.news_id in by_news else None,
            model_metadata={**event.model_metadata, "stage1_extractor": "bge_small_zh"},
        )
        for event in rule_output.events
    )
    diagnostics = dict(rule_output.diagnostics)
    diagnostics.update(
        {
            "model": "bge_small_zh",
            "embedding_model": text_cfg.model_name,
            "embedding_count": len(embeddings),
            "local_text_fallback_used": any(bool(signal.model_metadata.get("fallback_used")) for signal in embeddings),
        }
    )
    return Stage1Output(
        items=rule_output.items,
        sentiments=rule_output.sentiments,
        events=events,
        sector_impacts=rule_output.sector_impacts,
        bl_views=rule_output.bl_views,
        fallback_used=rule_output.fallback_used,
        diagnostics=diagnostics,
    )


def _model_config(cfg: Stage1Config, model_name: str) -> TextModelConfig:
    base = cfg.text_model
    return TextModelConfig(
        enabled=True,
        provider=base.provider,
        model_name=base.model_name or model_name,
        local_path=base.local_path,
        revision=base.revision,
        offline_only=base.offline_only,
        fallback=base.fallback,
        max_length=base.max_length,
        embedding_dims=base.embedding_dims,
    )
