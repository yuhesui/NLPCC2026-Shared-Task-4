from __future__ import annotations

from pathlib import Path
import sys


PACKAGE_ROOT = Path(__file__).resolve().parents[3]
if str(PACKAGE_ROOT) in sys.path:
    sys.path.remove(str(PACKAGE_ROOT))
sys.path.insert(0, str(PACKAGE_ROOT))

from agent_platform.agents.track_a_a2_real_submission_agent import TrackAA2RealSubmissionAgent
from agent_platform.agents.track_b_b2_real_submission_agent import TrackBB2RealSubmissionAgent
from nlpcc.news_overlay.production_tensor import BGE_SNAPSHOT, FINBERT_SNAPSHOT


def test_submission_models_are_inside_package_root() -> None:
    assert BGE_SNAPSHOT.is_dir()
    assert FINBERT_SNAPSHOT.is_dir()
    assert PACKAGE_ROOT in BGE_SNAPSHOT.parents
    assert PACKAGE_ROOT in FINBERT_SNAPSHOT.parents


def test_submission_agents_pin_fixed_candidates_and_local_paths() -> None:
    track_a = TrackAA2RealSubmissionAgent()
    track_b = TrackBB2RealSubmissionAgent()

    assert (track_a.track, track_a.candidate_id) == ("macro", "A2_real")
    assert (track_b.track, track_b.candidate_id) == ("sector", "B2_real")
    for agent in (track_a, track_b):
        assert PACKAGE_ROOT in Path(agent.candidate_config["bge_path"]).parents
        assert PACKAGE_ROOT in Path(agent.candidate_config["finbert_path"]).parents
        assert agent.candidate_config["local_files_only"] is True
        assert agent.candidate_config["allow_proxy_news"] is False
        assert agent.candidate_config["allow_fixed_target_replay"] is False


def test_selected_agents_make_local_decision_without_news_proxy() -> None:
    history = {
        "000300.SH": [
            {"date": "2025-01-01", "date_int": 20250101, "close": 100.0},
            {"date": "2025-01-02", "date_int": 20250102, "open": 101.0, "close": None},
        ],
        "000012.SH": [
            {"date": "2025-01-01", "date_int": 20250101, "close": 100.0},
            {"date": "2025-01-02", "date_int": 20250102, "open": 100.0, "close": None},
        ],
    }
    agent = TrackAA2RealSubmissionAgent()
    decision = agent.decide(
        date_to_decision="2025-01-02",
        historical_prices=history,
        current_portfolio={"cash": 100000.0, "holdings": {}, "total_value": 100000.0},
        news_data=[],
        fund_pool=list(history),
    )
    assert decision["metadata"]["proxy_mode"] is False
    assert decision["metadata"]["fixed_target_replay_used"] is False
    assert abs(sum(decision["target_weights"].values()) - 0.97) < 1e-9
