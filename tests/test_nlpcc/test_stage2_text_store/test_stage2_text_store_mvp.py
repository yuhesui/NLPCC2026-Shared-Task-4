from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage1_news.schema import BLView, EventTuple, Stage1Output
from nlpcc.stage2_text_store.models.confidence_matrix import build_confidence_matrix
from nlpcc.stage2_text_store.models.decayed_event_memory import build_decayed_event_memory, decay_weight
from nlpcc.stage2_text_store.models.event_table import build_event_table
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.schema import BLViewRecord
from nlpcc.stage2_text_store.validators import assert_valid_stage2_state


def _toy_news() -> list[dict]:
    return [
        {
            "SOURCE": "toy",
            "TITLE": "Policy support boosts semiconductor and AI growth",
            "CONTENT": "State Council stimulus and subsidy support technology demand recovery.",
            "RANKING": "1",
            "THEDATE": "2025-01-03",
            "PUBLISH_TIME": "2025-01-03 14:30:00",
        },
        {
            "SOURCE": "toy",
            "TITLE": "Property default risk pressures bank shares",
            "CONTENT": "Real estate default risk may hurt financials.",
            "RANKING": "2",
            "THEDATE": "2025-01-03",
            "PUBLISH_TIME": "2025-01-03 14:45:00",
        },
    ]


def test_stage2_consumes_stage1_output_and_emits_valid_state() -> None:
    stage1_output = run_stage1_news_pipeline(_toy_news(), decision_date=20250103)

    state = build_stage2_text_state(stage1_output, as_of_date=20250103)

    assert_valid_stage2_state(state)
    assert state.flat_features
    assert state.event_table
    assert state.bl_views
    assert state.confidence_matrix.labels
    assert state.decayed_memory.features
    assert state.as_dict() == build_stage2_text_state(stage1_output, as_of_date=20250103).as_dict()


def test_missing_stage1_output_returns_empty_valid_state() -> None:
    state = build_stage2_text_state(None, as_of_date=20250103)

    assert_valid_stage2_state(state)
    assert state.flat_features == ()
    assert state.event_table == ()
    assert state.bl_views == ()
    assert state.decayed_memory.features == {}
    assert state.diagnostics["missing_stage1_output"] is True


def test_duplicate_events_are_merged_deterministically() -> None:
    event = EventTuple(
        news_id="n1",
        event_type="policy_support",
        entities=("AI",),
        sectors=("technology",),
        direction="positive",
        intensity=0.6,
        confidence=0.7,
        evidence="policy support",
    )
    stage1_output = Stage1Output(
        items=(),
        sentiments=(),
        events=(event, event),
        sector_impacts=(),
        bl_views=(),
    )

    rows = build_event_table(stage1_output)

    assert len(rows) == 1
    assert rows[0].duplicate_count == 2
    assert rows[0].signed_intensity == 0.6
    assert rows == build_event_table(stage1_output)


def test_confidence_matrix_clamps_bounds() -> None:
    views = (
        BLViewRecord("too_high:positive", "too_high", "positive", 10.0, 1.5, "unit"),
        BLViewRecord("too_low:negative", "too_low", "negative", -10.0, -0.2, "unit"),
    )

    matrix = build_confidence_matrix(views)

    assert matrix.labels == ("too_high", "too_low")
    assert matrix.values[0][0] == 1.0
    assert matrix.values[1][1] == 0.0
    assert matrix.values[0][1] == 0.0


def test_decayed_event_memory_is_deterministic_and_ablatable() -> None:
    event = EventTuple(
        news_id="n2",
        event_type="default_risk",
        entities=("bank",),
        sectors=("financials",),
        direction="negative",
        intensity=0.8,
        confidence=0.5,
        evidence="default risk",
    )
    stage1_output = Stage1Output(
        items=(),
        sentiments=(),
        events=(event,),
        sector_impacts=(),
        bl_views=(BLView("financials", "negative", -20.0, 0.5, "risk view"),),
    )
    event_table = build_event_table(stage1_output)
    ages = {event_table[0].event_id: 3.0}

    first = build_decayed_event_memory(event_table, as_of_date_int=20250106, half_life_days=3.0, age_days_by_event_id=ages)
    second = build_decayed_event_memory(event_table, as_of_date_int=20250106, half_life_days=3.0, age_days_by_event_id=ages)
    no_decay = build_decayed_event_memory(event_table, as_of_date_int=20250106, half_life_days=3.0)

    assert decay_weight(3.0, 3.0) == 0.5
    assert first.as_dict() == second.as_dict()
    assert first.features["memory.sector.financials.signal"] == -0.2
    assert no_decay.features["memory.sector.financials.signal"] == -0.4
