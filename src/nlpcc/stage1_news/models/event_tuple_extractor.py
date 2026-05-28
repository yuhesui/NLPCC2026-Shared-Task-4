"""Rule-based event tuple extraction."""

from __future__ import annotations

from nlpcc.stage1_news.models.entity_sector_mapper import map_text_to_entities, map_text_to_sectors
from nlpcc.stage1_news.schema import EventTuple, NormalizedNewsItem, SentimentSignal


EVENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "monetary_policy": ("rate cut", "liquidity", "pboc", "央行", "降息", "流动性"),
    "fiscal_policy": ("stimulus", "subsidy", "policy support", "财政", "补贴", "支持"),
    "earnings": ("profit", "revenue", "loss", "earnings", "盈利", "营收", "亏损"),
    "regulation": ("regulation", "crackdown", "approval", "监管", "整治", "审批"),
    "geopolitical": ("sanction", "tariff", "export control", "制裁", "关税", "出口管制"),
    "macro_growth": ("growth", "pmi", "recovery", "demand", "增长", "复苏", "需求"),
}


def extract_events(item: NormalizedNewsItem, sentiment: SentimentSignal) -> tuple[EventTuple, ...]:
    text = item.text.lower()
    sectors = map_text_to_sectors(item.text) or ("broad_equity",)
    entities = map_text_to_entities(item.text)
    event_types = [
        event_type
        for event_type, keywords in EVENT_KEYWORDS.items()
        if any(keyword.lower() in text for keyword in keywords)
    ] or ["general_news"]
    direction = sentiment.label
    intensity = min(1.0, 0.25 + abs(sentiment.score) * 0.55 + 0.05 * len(sectors))
    confidence = min(1.0, sentiment.confidence + 0.05 * len(event_types))
    return tuple(
        EventTuple(
            news_id=item.news_id,
            event_type=event_type,
            entities=entities,
            sectors=sectors,
            direction=direction,
            intensity=intensity,
            confidence=confidence,
            evidence=item.title[:180],
        )
        for event_type in event_types
    )
