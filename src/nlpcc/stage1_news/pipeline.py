"""Stage 1 news-processing orchestration."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from nlpcc.stage1_news.models.no_llm_fallback import no_llm_fallback_output
from nlpcc.stage1_news.models.rule_based_extractor import RuleBasedNewsExtractor
from nlpcc.stage1_news.schema import NormalizedNewsItem, Stage1Config, Stage1Output
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
    if not raw_news:
        output = no_llm_fallback_output("missing_news", cfg)
        assert_valid_stage1_output(output)
        return output

    normalized = normalize_news_items(tuple(raw_news))
    visible, diagnostics = filter_visible_news(normalized, decision_date=decision_date, top_rank=cfg.top_rank)
    if not visible:
        output = no_llm_fallback_output("no_visible_valid_news", cfg)
        output.diagnostics.update(diagnostics)
        assert_valid_stage1_output(output)
        return output
    output = RuleBasedNewsExtractor(cfg).extract(visible)
    output.diagnostics.update(diagnostics)
    assert_valid_stage1_output(output)
    return output
