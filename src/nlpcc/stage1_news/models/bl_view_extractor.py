"""Convert sector impacts into simple Black-Litterman-style views."""

from __future__ import annotations

from nlpcc.stage1_news.schema import BLView, SectorImpact


SECTOR_TO_ASSET_GROUP: dict[str, str] = {
    "broad_equity": "equity_beta",
    "technology": "technology_growth",
    "healthcare": "healthcare",
    "consumer": "consumer",
    "energy": "energy",
    "materials": "materials",
    "financials": "financials",
    "real_estate": "real_estate",
    "gold": "gold",
    "bonds": "bonds",
}


def extract_bl_views(impacts: tuple[SectorImpact, ...]) -> tuple[BLView, ...]:
    views: list[BLView] = []
    for impact in impacts:
        if impact.direction == "neutral" or impact.intensity <= 0:
            continue
        sign = 1.0 if impact.direction == "positive" else -1.0
        expected_return_bps = sign * round(50.0 * impact.intensity * impact.confidence, 4)
        views.append(
            BLView(
                asset_group=SECTOR_TO_ASSET_GROUP.get(impact.sector, impact.sector),
                direction=impact.direction,
                expected_return_bps=expected_return_bps,
                confidence=impact.confidence,
                rationale=f"{impact.sector} {impact.direction} impact from {impact.evidence_count} event(s)",
            )
        )
    return tuple(sorted(views, key=lambda view: (view.asset_group, view.direction)))
