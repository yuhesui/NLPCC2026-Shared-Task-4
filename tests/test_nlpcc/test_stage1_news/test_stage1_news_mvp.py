from datetime import datetime
from pathlib import Path

from nlpcc.stage1_news.cache import Stage1JsonCache, stage1_cache_key
from nlpcc.stage1_news.models.bl_view_extractor import extract_bl_views
from nlpcc.stage1_news.models.entity_sector_mapper import map_text_to_sectors
from nlpcc.stage1_news.models.llm_event_extractor import ControlledLLMEventExtractor
from nlpcc.stage1_news.models.no_llm_fallback import no_llm_fallback_output
from nlpcc.stage1_news.models.rule_based_extractor import RuleBasedNewsExtractor
from nlpcc.stage1_news.pipeline import normalize_news_items, run_stage1_news_pipeline
from nlpcc.stage1_news.schema import SectorImpact, Stage1Config
from nlpcc.stage1_news.validators import assert_valid_stage1_output


def _toy_news() -> list[dict]:
    return [
        {
            "SOURCE": "toy",
            "TITLE": "Policy support boosts semiconductor and AI growth",
            "CONTENT": "State Council stimulus and subsidy support technology demand recovery.",
            "RANKING": "1",
            "THEDATE": "2025-01-03",
            "PUBLISH_TIME": "2025-01-03 14:30:00",
        },
        {
            "SOURCE": "toy",
            "TITLE": "Property default risk pressures bank shares",
            "CONTENT": "Real estate default risk may hurt financials.",
            "RANKING": "2",
            "THEDATE": "2025-01-03",
            "PUBLISH_TIME": "2025-01-03 14:45:00",
        },
    ]


def test_rule_based_pipeline_produces_schema_valid_events_impacts_and_views() -> None:
    output = run_stage1_news_pipeline(_toy_news(), decision_date=20250103)

    assert_valid_stage1_output(output)
    assert output.fallback_used is False
    assert len(output.items) == 2
    assert output.events
    assert {impact.sector for impact in output.sector_impacts} & {"technology", "financials", "real_estate"}
    assert output.bl_views
    assert all(0.0 <= view.confidence <= 1.0 for view in output.bl_views)


def test_cutoff_and_future_news_are_filtered_before_extraction() -> None:
    news = _toy_news() + [
        {
            "SOURCE": "toy",
            "TITLE": "Late market close rumor should be invisible",
            "CONTENT": "This should not be visible at decision time.",
            "RANKING": "3",
            "THEDATE": "2025-01-03",
            "PUBLISH_TIME": "2025-01-03 15:00:00",
        },
        {
            "SOURCE": "toy",
            "TITLE": "Future policy support",
            "CONTENT": "Future news should be filtered.",
            "RANKING": "4",
            "THEDATE": "2025-01-04",
            "PUBLISH_TIME": "2025-01-04 09:00:00",
        },
    ]

    output = run_stage1_news_pipeline(news, decision_date=20250103)

    assert len(output.items) == 2
    assert output.diagnostics["filtered_after_cutoff"] == 1
    assert output.diagnostics["filtered_future"] == 1


def test_missing_or_invalid_news_uses_valid_no_llm_fallback() -> None:
    output = run_stage1_news_pipeline([], decision_date=20250103)
    invalid = run_stage1_news_pipeline([{"TITLE": "", "CONTENT": "", "RANKING": "1"}], decision_date=20250103)
    direct = no_llm_fallback_output("unit_test")

    assert output.fallback_used is True
    assert invalid.fallback_used is True
    assert direct.diagnostics["model"] == "no_llm_fallback"
    assert_valid_stage1_output(output)
    assert_valid_stage1_output(invalid)


def test_model_components_are_deterministic() -> None:
    items = normalize_news_items(tuple(_toy_news()))
    first = RuleBasedNewsExtractor(Stage1Config()).extract(items)
    second = RuleBasedNewsExtractor(Stage1Config()).extract(items)
    sectors = map_text_to_sectors("AI semiconductor software support")
    views = extract_bl_views((SectorImpact("technology", "positive", 0.5, 0.8, 2),))

    assert first.as_dict() == second.as_dict()
    assert "technology" in sectors
    assert views[0].asset_group == "technology_growth"
    assert views[0].expected_return_bps > 0


def test_controlled_llm_extractor_is_optional_and_falls_back_without_callable() -> None:
    items = normalize_news_items(tuple(_toy_news()))
    extractor = ControlledLLMEventExtractor(Stage1Config(use_llm=False))

    output = extractor.extract(items)

    assert output.fallback_used is True
    assert output.diagnostics["fallback_reason"] == "llm_disabled_or_unavailable"


def test_stage1_cache_key_and_json_cache_are_deterministic() -> None:
    payload = {"news": _toy_news(), "decision_date": 20250103}
    key = stage1_cache_key(payload)
    cache = Stage1JsonCache(Path("outputs/test_stage1_cache"))
    cache.set(key, {"created": datetime(2025, 1, 3, 14, 30).isoformat(), "value": 1})

    assert key == stage1_cache_key(payload)
    assert cache.get(key)["value"] == 1
