"""Rule-based Stage 1 extractor."""

from __future__ import annotations

from dataclasses import dataclass

from nlpcc.stage1_news.models.bl_view_extractor import extract_bl_views
from nlpcc.stage1_news.models.event_tuple_extractor import extract_events
from nlpcc.stage1_news.models.no_llm_fallback import no_llm_fallback_output
from nlpcc.stage1_news.models.sector_impact_extractor import extract_sector_impacts
from nlpcc.stage1_news.models.sentiment_classifier import classify_sentiment
from nlpcc.stage1_news.schema import NormalizedNewsItem, Stage1Config, Stage1Output


@dataclass(frozen=True)
class RuleBasedNewsExtractor:
    config: Stage1Config = Stage1Config()

    def extract(self, items: tuple[NormalizedNewsItem, ...]) -> Stage1Output:
        if not items:
            return no_llm_fallback_output("no_visible_news", self.config)
        sentiments = tuple(classify_sentiment(item) for item in items)
        events = tuple(event for item, sentiment in zip(items, sentiments) for event in extract_events(item, sentiment))
        sector_impacts = extract_sector_impacts(events)
        bl_views = extract_bl_views(sector_impacts)
        return Stage1Output(
            items=items,
            sentiments=sentiments,
            events=events,
            sector_impacts=sector_impacts,
            bl_views=bl_views,
            fallback_used=False,
            diagnostics={
                "model": "rule_based",
                "item_count": len(items),
                "event_count": len(events),
                "sector_impact_count": len(sector_impacts),
                "bl_view_count": len(bl_views),
            },
        )
