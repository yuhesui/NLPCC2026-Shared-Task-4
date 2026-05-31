"""Rank feature panel for Track 2 deterministic ranking models."""

from __future__ import annotations

from typing import Any

from nlpcc.stage1_news.models.entity_sector_mapper import map_sectors_to_track2_etfs
from nlpcc.stage2_text_store.schema import SectorImpactRow


def build_rank_feature_panel(
    sector_panel: tuple[SectorImpactRow, ...],
    knowledge_graph: dict[str, Any] | None = None,
    retrieval_index: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], ...]:
    graph_scores = dict((knowledge_graph or {}).get("activation_by_asset", {}) or {})
    sector_analogue = _analogue_by_sector(retrieval_index or {})
    rows: dict[str, dict[str, Any]] = {}
    for impact in sector_panel:
        mapped_assets = impact.etf_ids or map_sectors_to_track2_etfs((impact.sector,))
        for asset in mapped_assets:
            row = rows.setdefault(
                asset,
                {
                    "asset": asset,
                    "sector_score": 0.0,
                    "sentiment_score": 0.0,
                    "graph_score": 0.0,
                    "analogue_score": 0.0,
                    "evidence_count": 0,
                },
            )
            row["sector_score"] += impact.signed_intensity * impact.confidence
            row["sentiment_score"] += 1.0 if impact.direction == "positive" else -1.0 if impact.direction == "negative" else 0.0
            row["evidence_count"] += impact.evidence_count
            row["analogue_score"] += sector_analogue.get(impact.sector, 0.0)
    for asset, score in graph_scores.items():
        row = rows.setdefault(
            asset,
            {
                "asset": asset,
                "sector_score": 0.0,
                "sentiment_score": 0.0,
                "graph_score": 0.0,
                "analogue_score": 0.0,
                "evidence_count": 0,
            },
        )
        row["graph_score"] = score
    return tuple({key: round(value, 8) if isinstance(value, float) else value for key, value in row.items()} for row in rows.values())


def _analogue_by_sector(index: dict[str, Any]) -> dict[str, float]:
    scores: dict[str, float] = {}
    weights: dict[str, float] = {}
    for row in index.get("rows", []):
        sector = str(row.get("sector") or "unknown")
        confidence = float(row.get("confidence", 0.0) or 0.0)
        scores[sector] = scores.get(sector, 0.0) + float(row.get("signed_intensity", 0.0) or 0.0) * confidence
        weights[sector] = weights.get(sector, 0.0) + confidence
    return {sector: scores[sector] / max(weights.get(sector, 0.0), 1e-9) for sector in scores}
