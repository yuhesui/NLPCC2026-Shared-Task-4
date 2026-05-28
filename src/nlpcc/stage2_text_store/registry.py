"""Stage 2 model registry."""

from __future__ import annotations

from collections.abc import Callable

from nlpcc.stage2_text_store.models.bl_view_store import build_bl_view_store
from nlpcc.stage2_text_store.models.confidence_matrix import build_confidence_matrix
from nlpcc.stage2_text_store.models.decayed_event_memory import build_decayed_event_memory
from nlpcc.stage2_text_store.models.event_table import build_event_table
from nlpcc.stage2_text_store.models.flat_feature_table import build_flat_feature_table


STAGE2_MODEL_REGISTRY: dict[str, Callable[..., object]] = {
    "flat_feature_table": build_flat_feature_table,
    "event_table": build_event_table,
    "bl_view_store": build_bl_view_store,
    "confidence_matrix": build_confidence_matrix,
    "decayed_event_memory": build_decayed_event_memory,
}


def get_stage2_model(name: str) -> Callable[..., object]:
    try:
        return STAGE2_MODEL_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(STAGE2_MODEL_REGISTRY))
        raise KeyError(f"Unknown Stage 2 model '{name}'. Available: {available}") from exc
