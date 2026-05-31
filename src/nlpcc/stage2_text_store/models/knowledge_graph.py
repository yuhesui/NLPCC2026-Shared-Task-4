"""Lightweight deterministic sector-to-ETF graph for Stage 2."""

from __future__ import annotations

from nlpcc.stage1_news.models.entity_sector_mapper import map_sectors_to_track2_etfs
from typing import Any

from nlpcc.stage2_text_store.schema import EventTableRow, SectorGraphEdge, SectorImpactRow


def build_knowledge_graph_stub() -> dict[str, str]:
    return {
        "status": "available_mvp",
        "component": "knowledge_graph",
        "reason": "Use build_knowledge_graph_lite for deterministic sector-policy graph activations.",
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


def build_knowledge_graph_lite(
    sector_panel: tuple[SectorImpactRow, ...],
    event_table: tuple[EventTableRow, ...] = (),
) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    activation_by_sector: dict[str, float] = {}
    for row in sector_panel:
        nodes.setdefault(row.sector, {"id": row.sector, "type": "sector"})
        activation_by_sector[row.sector] = activation_by_sector.get(row.sector, 0.0) + row.signed_intensity * row.confidence
        for etf_id in row.etf_ids or map_sectors_to_track2_etfs((row.sector,)):
            nodes.setdefault(etf_id, {"id": etf_id, "type": "asset"})
            edges.append(
                {
                    "source": row.sector,
                    "target": etf_id,
                    "relation": "sector_to_etf",
                    "weight": round(abs(row.signed_intensity) * row.confidence, 8),
                    "direction": row.direction,
                }
            )
    for event in event_table:
        policy_node = f"event:{event.event_type}"
        nodes.setdefault(policy_node, {"id": policy_node, "type": "event_type"})
        nodes.setdefault(event.sector, {"id": event.sector, "type": "sector"})
        edges.append(
            {
                "source": policy_node,
                "target": event.sector,
                "relation": "event_impacts_sector",
                "weight": round(abs(event.signed_intensity) * event.confidence, 8),
                "direction": event.direction,
            }
        )
    activation_by_asset: dict[str, float] = {}
    for edge in edges:
        if edge["relation"] != "sector_to_etf":
            continue
        source = str(edge["source"])
        target = str(edge["target"])
        activation_by_asset[target] = activation_by_asset.get(target, 0.0) + activation_by_sector.get(source, 0.0)
    return {
        "status": "available_mvp",
        "component": "knowledge_graph_lite",
        "nodes": tuple(nodes.values()),
        "edges": tuple(edges),
        "activation_by_sector": {key: round(value, 8) for key, value in activation_by_sector.items()},
        "activation_by_asset": {key: round(value, 8) for key, value in activation_by_asset.items()},
    }
