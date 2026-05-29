from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state
from nlpcc.stage2_text_store.validators import assert_valid_stage2_state


def test_stage2_builds_sector_impact_panel_and_sector_etf_graph() -> None:
    stage1 = run_stage1_news_pipeline(
        [
            {
                "SOURCE": "toy",
                "TITLE": "Bank insurance and securities rally after policy support",
                "CONTENT": "Financial policy support improves brokerage, banking and insurance sentiment.",
                "RANKING": "1",
                "THEDATE": "2025-01-03",
                "PUBLISH_TIME": "2025-01-03 14:30:00",
            }
        ],
        decision_date=20250103,
    )

    state = build_stage2_text_state(stage1, as_of_date=20250103)

    assert_valid_stage2_state(state)
    assert state.sector_impact_panel
    assert state.sector_graph_edges
    graph_targets = {edge.target for edge in state.sector_graph_edges}
    assert {"512880.SH", "512800.SH", "512070.SH"} & graph_targets
