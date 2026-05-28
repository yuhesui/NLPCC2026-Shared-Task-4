"""Stage 1 schema validators."""

from __future__ import annotations

from dataclasses import dataclass

from nlpcc.stage1_news.schema import BLView, EventTuple, NormalizedNewsItem, SectorImpact, Stage1Output


class Stage1ValidationError(ValueError):
    """Raised when Stage 1 output violates schema constraints."""


@dataclass(frozen=True)
class Stage1ValidationIssue:
    code: str
    message: str
    location: str | None = None


def _bounded(value: float, low: float = 0.0, high: float = 1.0) -> bool:
    return low <= value <= high


def validate_news_item(item: NormalizedNewsItem, location: str) -> list[Stage1ValidationIssue]:
    issues: list[Stage1ValidationIssue] = []
    if not item.news_id:
        issues.append(Stage1ValidationIssue("missing_news_id", "News item has no id.", location))
    if not item.text:
        issues.append(Stage1ValidationIssue("empty_news_text", "News item has no title/content text.", location))
    if item.ranking is not None and item.ranking < 1:
        issues.append(Stage1ValidationIssue("invalid_ranking", "Ranking must be positive.", location))
    return issues


def validate_event(event: EventTuple, location: str) -> list[Stage1ValidationIssue]:
    issues: list[Stage1ValidationIssue] = []
    if event.direction not in {"positive", "negative", "neutral"}:
        issues.append(Stage1ValidationIssue("invalid_direction", "Event direction is invalid.", location))
    if not _bounded(event.intensity):
        issues.append(Stage1ValidationIssue("invalid_intensity", "Event intensity must be in [0, 1].", location))
    if not _bounded(event.confidence):
        issues.append(Stage1ValidationIssue("invalid_confidence", "Event confidence must be in [0, 1].", location))
    return issues


def validate_sector_impact(impact: SectorImpact, location: str) -> list[Stage1ValidationIssue]:
    issues: list[Stage1ValidationIssue] = []
    if not impact.sector:
        issues.append(Stage1ValidationIssue("missing_sector", "Sector impact has no sector.", location))
    if not _bounded(impact.intensity):
        issues.append(Stage1ValidationIssue("invalid_intensity", "Sector intensity must be in [0, 1].", location))
    if not _bounded(impact.confidence):
        issues.append(Stage1ValidationIssue("invalid_confidence", "Sector confidence must be in [0, 1].", location))
    return issues


def validate_bl_view(view: BLView, location: str) -> list[Stage1ValidationIssue]:
    issues: list[Stage1ValidationIssue] = []
    if not view.asset_group:
        issues.append(Stage1ValidationIssue("missing_asset_group", "BL view has no asset group.", location))
    if not _bounded(view.confidence):
        issues.append(Stage1ValidationIssue("invalid_confidence", "BL view confidence must be in [0, 1].", location))
    return issues


def find_stage1_output_issues(output: Stage1Output) -> list[Stage1ValidationIssue]:
    issues: list[Stage1ValidationIssue] = []
    for index, item in enumerate(output.items):
        issues.extend(validate_news_item(item, f"items[{index}]"))
    for index, event in enumerate(output.events):
        issues.extend(validate_event(event, f"events[{index}]"))
    for index, impact in enumerate(output.sector_impacts):
        issues.extend(validate_sector_impact(impact, f"sector_impacts[{index}]"))
    for index, view in enumerate(output.bl_views):
        issues.extend(validate_bl_view(view, f"bl_views[{index}]"))
    return issues


def assert_valid_stage1_output(output: Stage1Output) -> None:
    issues = find_stage1_output_issues(output)
    if issues:
        joined = "; ".join(f"{issue.code}@{issue.location}: {issue.message}" for issue in issues)
        raise Stage1ValidationError(joined)
