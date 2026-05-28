"""Stage 2 quantified text-store orchestration."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from nlpcc.stage1_news.schema import Stage1Output
from nlpcc.stage2_text_store.models.bl_view_store import build_bl_view_store
from nlpcc.stage2_text_store.models.confidence_matrix import build_confidence_matrix
from nlpcc.stage2_text_store.models.decayed_event_memory import build_decayed_event_memory
from nlpcc.stage2_text_store.models.event_table import build_event_table
from nlpcc.stage2_text_store.models.flat_feature_table import build_flat_feature_table
from nlpcc.stage2_text_store.schema import ConfidenceMatrix, DecayedEventMemory, Stage2Config, Stage2TextState
from nlpcc.stage2_text_store.validators import assert_valid_stage2_state


def _date_to_int(value: int | str | date | datetime | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return int(value.strftime("%Y%m%d"))
    if isinstance(value, date):
        return int(value.strftime("%Y%m%d"))
    text = str(value).replace("-", "")
    if len(text) >= 8 and text[:8].isdigit():
        return int(text[:8])
    return None


def _infer_date_int(stage1_output: Stage1Output | None, explicit: int | str | date | datetime | None) -> int | None:
    resolved = _date_to_int(explicit)
    if resolved is not None:
        return resolved
    if stage1_output is None:
        return None
    candidates: list[int] = []
    for item in stage1_output.items:
        if item.trade_date:
            candidates.append(int(item.trade_date.strftime("%Y%m%d")))
        elif item.publish_time:
            candidates.append(int(item.publish_time.strftime("%Y%m%d")))
    return max(candidates) if candidates else None


def empty_stage2_text_state(
    *,
    as_of_date_int: int | None = None,
    decay_half_life_days: float = Stage2Config().decay_half_life_days,
    diagnostics: dict[str, Any] | None = None,
) -> Stage2TextState:
    state = Stage2TextState(
        flat_features=(),
        event_table=(),
        bl_views=(),
        confidence_matrix=ConfidenceMatrix(labels=(), values=()),
        decayed_memory=DecayedEventMemory(
            as_of_date_int=as_of_date_int,
            features={},
            decay_half_life_days=decay_half_life_days,
            event_count=0,
        ),
        diagnostics=diagnostics or {},
    )
    assert_valid_stage2_state(state)
    return state


def build_stage2_text_state(
    stage1_output: Stage1Output | None,
    *,
    as_of_date: int | str | date | datetime | None = None,
    config: Stage2Config | dict[str, Any] | None = None,
    event_age_days: dict[str, float] | None = None,
) -> Stage2TextState:
    """Build the deterministic Stage 2 state consumed by later stages."""

    cfg = config if isinstance(config, Stage2Config) else Stage2Config.from_mapping(config)
    as_of_date_int = _infer_date_int(stage1_output, as_of_date)
    if stage1_output is None:
        return empty_stage2_text_state(
            as_of_date_int=as_of_date_int,
            decay_half_life_days=cfg.decay_half_life_days,
            diagnostics={"missing_stage1_output": True},
        )

    event_table = build_event_table(stage1_output)
    flat_features = build_flat_feature_table(stage1_output, date_int=as_of_date_int)
    bl_views = build_bl_view_store(stage1_output)
    confidence_matrix = build_confidence_matrix(
        bl_views,
        min_confidence=cfg.min_confidence,
        max_confidence=cfg.max_confidence,
    )
    decayed_memory = build_decayed_event_memory(
        event_table,
        as_of_date_int=as_of_date_int,
        half_life_days=cfg.decay_half_life_days,
        age_days_by_event_id=event_age_days,
    )
    diagnostics = {
        "stage1_fallback_used": stage1_output.fallback_used,
        "source_news_count": len(stage1_output.items),
        "source_event_count": len(stage1_output.events),
    }
    diagnostics.update(stage1_output.diagnostics)
    state = Stage2TextState(
        flat_features=flat_features,
        event_table=event_table,
        bl_views=bl_views,
        confidence_matrix=confidence_matrix,
        decayed_memory=decayed_memory,
        diagnostics=diagnostics,
    )
    assert_valid_stage2_state(state)
    return state
