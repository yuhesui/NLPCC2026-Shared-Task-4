"""Lightweight deterministic sector-to-ETF graph for Stage 2."""

from __future__ import annotations

from nlpcc.stage1_news.models.entity_sector_mapper import map_sectors_to_track2_etfs
from nlpcc.stage2_text_store.schema import SectorGraphEdge, SectorImpactRow


def build_knowledge_graph_stub() -> dict[str, str]:
    return {
        "status": "deferred",
        "component": "knowledge_graph",
        "reason": "Knowledge graph construction is deferred until the tabular text state is stable.",
    }


def build_sector_etf_graph(sector_panel: tuple[SectorImpactRow, ...]) -> tuple[SectorGraphEdge, ...]:
    edges: list[SectorGraphEdge] = []
    sectors = tuple(row.sector for row in sector_panel)
    mapped = {sector: map_sectors_to_track2_etfs((sector,)) for sector in sectors}
    for sector in sorted(mapped):
        for etf_id in mapped[sector]:
            source_row = next((row for row in sector_panel if row.sector == sector), None)
            weight = abs(source_row.signed_intensity) if source_row else 0.0
            confidence = source_row.confidence if source_row else 0.0
            edges.append(
                SectorGraphEdge(
                    source=sector,
                    target=etf_id,
                    relation="sector_to_etf",
                    weight=round(weight, 8),
                    confidence=round(confidence, 8),
                )
            )
    return tuple(edges)
