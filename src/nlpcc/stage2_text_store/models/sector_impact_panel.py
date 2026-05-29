"""Sector impact panel and ETF mapping for Track 2."""

from __future__ import annotations

from nlpcc.stage1_news.models.entity_sector_mapper import map_sectors_to_track2_etfs
from nlpcc.stage1_news.models.sector_impact_extractor import sector_impact_score
from nlpcc.stage1_news.schema import Stage1Output
from nlpcc.stage2_text_store.schema import SectorImpactRow


def build_sector_impact_panel(stage1_output: Stage1Output | None) -> tuple[SectorImpactRow, ...]:
    if stage1_output is None:
        return ()
    rows: list[SectorImpactRow] = []
    for impact in sorted(stage1_output.sector_impacts, key=lambda item: item.sector):
        etfs = map_sectors_to_track2_etfs((impact.sector,))
        rows.append(
            SectorImpactRow(
                sector=impact.sector,
                direction=impact.direction,
                signed_intensity=round(sector_impact_score(impact), 8),
                confidence=round(impact.confidence, 8),
                evidence_count=impact.evidence_count,
                etf_ids=etfs,
            )
        )
    return tuple(rows)
