"""Stage 1 extractor registry."""

from __future__ import annotations

from typing import Callable

from nlpcc.stage1_news.models.bl_view_extractor import extract_bl_views
from nlpcc.stage1_news.models.event_tuple_extractor import extract_events
from nlpcc.stage1_news.models.no_llm_fallback import no_llm_fallback_output
from nlpcc.stage1_news.models.rule_based_extractor import RuleBasedNewsExtractor
from nlpcc.stage1_news.models.sector_impact_extractor import extract_sector_impacts
from nlpcc.stage1_news.models.sentiment_classifier import classify_sentiment


STAGE1_MODELS: dict[str, Callable] = {
    "rule_based": RuleBasedNewsExtractor,
    "sentiment_classifier": classify_sentiment,
    "event_tuple_extractor": extract_events,
    "sector_impact_extractor": extract_sector_impacts,
    "bl_view_extractor": extract_bl_views,
    "no_llm_fallback": no_llm_fallback_output,
}


def get_stage1_model(name: str) -> Callable:
    try:
        return STAGE1_MODELS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown Stage 1 model: {name!r}") from exc
