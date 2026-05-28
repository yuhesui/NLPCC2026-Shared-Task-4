"""Derived belief-state helpers for Stage 4 consumers."""

from __future__ import annotations

from nlpcc.stage2_text_store.schema import BLViewRecord, DecayedEventMemory, FlatFeatureRow


def build_belief_state(
    flat_features: tuple[FlatFeatureRow, ...],
    bl_views: tuple[BLViewRecord, ...],
    decayed_memory: DecayedEventMemory,
) -> dict[str, float | int]:
    """Return a compact numeric summary for lightweight agents."""

    feature_map = {row.feature_name: row.value for row in flat_features}
    expected_return_sum = round(sum(view.expected_return_bps * view.confidence for view in bl_views), 8)
    memory_signal_sum = round(sum(decayed_memory.features.values()), 8)
    return {
        "news_item_count": int(feature_map.get("news.item_count", 0.0)),
        "event_count": int(feature_map.get("news.event_count", 0.0)),
        "bl_view_count": int(feature_map.get("news.bl_view_count", 0.0)),
        "weighted_expected_return_bps": expected_return_sum,
        "memory_signal_sum": memory_signal_sum,
    }
