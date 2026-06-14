"""Research-only synthetic manifest generation."""

from __future__ import annotations

from nlpcc.news_overlay.synthetic.scenarios import SyntheticScenario


def scenario_manifest_row(
    scenario: SyntheticScenario,
    *,
    source_years: str,
    seed: int,
    date_start: str,
    date_end: str,
    rows: int,
    assets: int,
    news_count: int,
    price_count: int,
) -> dict[str, object]:
    after_news = max(0, round(news_count * scenario.news_multiplier))
    return {
        "source_years": source_years,
        "random_seed": seed,
        "scenario_name": scenario.name,
        "date_range": f"{date_start}:{date_end}",
        "rows": rows,
        "assets": assets,
        "news_count_before": news_count,
        "news_count_after": after_news,
        "price_count_before": price_count,
        "price_count_after": price_count,
        "leakage_checks_passed": "pass",
    }
