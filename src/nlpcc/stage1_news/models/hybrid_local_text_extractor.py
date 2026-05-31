"""Hybrid rule + local FinBERT/BGE Stage 1 extractor."""

from __future__ import annotations

from dataclasses import dataclass, replace

from nlpcc.stage1_news.cache import stage1_cache_key
from nlpcc.stage1_news.models.bge_small_zh_extractor import (
    BgeSmallZhEmbeddingExtractor,
    DEFAULT_BGE_MODEL,
    EmbeddingSignal,
)
from nlpcc.stage1_news.models.finbert_tone_chinese_extractor import (
    DEFAULT_FINBERT_MODEL,
    FinbertToneChineseSentimentExtractor,
)
from nlpcc.stage1_news.models.rule_based_extractor import RuleBasedNewsExtractor
from nlpcc.stage1_news.schema import NormalizedNewsItem, Stage1Config, Stage1Output
from nlpcc.stage1_news.text_model_config import TextModelConfig


@dataclass(frozen=True)
class HybridLocalTextExtractor:
    config: Stage1Config

    def extract(self, items: tuple[NormalizedNewsItem, ...]) -> Stage1Output:
        rule_output = RuleBasedNewsExtractor(self.config).extract(items)
        finbert_cfg = _child_config(
            self.config.text_model,
            model_name=DEFAULT_FINBERT_MODEL,
            fallback=self.config.text_model.fallback,
        )
        bge_cfg = _child_config(
            self.config.text_model,
            model_name=DEFAULT_BGE_MODEL,
            fallback=self.config.text_model.fallback,
        )
        sentiments = FinbertToneChineseSentimentExtractor(finbert_cfg).classify_items(items)
        embeddings = BgeSmallZhEmbeddingExtractor(bge_cfg).embed_items(items)
        embedding_by_news = {signal.news_id: signal for signal in embeddings}
        event_output = tuple(
            replace(
                event,
                relevance_score=_embedding_relevance(embedding_by_news.get(event.news_id)),
                embedding_ref=_embedding_ref(embedding_by_news.get(event.news_id)),
                model_metadata={
                    **event.model_metadata,
                    "stage1_extractor": "hybrid_rule_bge_finbert",
                },
            )
            for event in rule_output.events
        )
        diagnostics = dict(rule_output.diagnostics)
        diagnostics.update(
            {
                "model": "hybrid_rule_bge_finbert",
                "sentiment_model": DEFAULT_FINBERT_MODEL,
                "embedding_model": DEFAULT_BGE_MODEL,
                "embedding_count": len(embeddings),
                "cache_key": stage1_cache_key([item.raw for item in items], version="prompt15_hybrid_local_text_v1")[:16],
                "local_text_fallback_used": any(
                    bool(signal.model_metadata.get("fallback_used")) for signal in sentiments
                )
                or any(bool(signal.model_metadata.get("fallback_used")) for signal in embeddings),
            }
        )
        return Stage1Output(
            items=rule_output.items,
            sentiments=sentiments,
            events=event_output,
            sector_impacts=rule_output.sector_impacts,
            bl_views=rule_output.bl_views,
            fallback_used=rule_output.fallback_used,
            diagnostics=diagnostics,
        )


def _child_config(config: TextModelConfig, *, model_name: str, fallback: str) -> TextModelConfig:
    resolved_model = config.model_name if config.model_name and config.model_name not in {DEFAULT_BGE_MODEL, DEFAULT_FINBERT_MODEL} else model_name
    return TextModelConfig(
        enabled=True,
        provider=config.provider,
        model_name=resolved_model,
        local_path=config.local_path,
        revision=config.revision,
        offline_only=config.offline_only,
        fallback=fallback,
        max_length=config.max_length,
        embedding_dims=config.embedding_dims,
    )


def _embedding_relevance(signal: EmbeddingSignal | None) -> float:
    return round(float(signal.relevance_score), 6) if signal else 0.0


def _embedding_ref(signal: EmbeddingSignal | None) -> str | None:
    return signal.embedding_ref if signal else None
