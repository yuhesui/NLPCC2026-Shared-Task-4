from nlpcc.stage1_news.models.entity_sector_mapper import map_sectors_to_track2_etfs, map_text_to_sectors
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline


def test_track2_sector_mapper_links_text_to_public_etfs() -> None:
    sectors = map_text_to_sectors("semiconductor AI software policy support boosts technology demand")
    etfs = map_sectors_to_track2_etfs(sectors)

    assert {"technology", "semiconductor", "ai", "software"} & set(sectors)
    assert "159995.SZ" in etfs
    assert "159819.SZ" in etfs
    assert "159852.SZ" in etfs


def test_stage1_sector_impacts_include_track2_detail_sectors() -> None:
    output = run_stage1_news_pipeline(
        [
            {
                "SOURCE": "toy",
                "TITLE": "AI semiconductor policy support lifts software demand",
                "CONTENT": "Subsidy support for artificial intelligence, chip and software companies.",
                "RANKING": "1",
                "THEDATE": "2025-01-03",
                "PUBLISH_TIME": "2025-01-03 14:30:00",
            }
        ],
        decision_date=20250103,
    )

    sectors = {impact.sector for impact in output.sector_impacts}
    assert {"ai", "semiconductor", "software"} & sectors
    assert output.bl_views
