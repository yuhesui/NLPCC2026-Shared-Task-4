from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
from typing import Any


FINAL_TRACK = "sector"
FINAL_CANDIDATE_ID = "B2_real"
FINAL_CANDIDATE = "G15B"
PATH_KEYS = {"bge_path", "finbert_path", "reranker_path"}


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
AGENT_ROOT = PACKAGE_ROOT / "agent_platform" / "agents"
for path in (AGENT_ROOT, PACKAGE_ROOT):
    if str(path) in sys.path:
        sys.path.remove(str(path))
    sys.path.insert(0, str(path))

from nlpcc.execution.official_adapter import normalize_track  # noqa: E402
from prompt09_real_transformer_agent import Prompt09RealTransformerAgent  # noqa: E402


def _default_config_path() -> Path:
    sibling = Path(__file__).resolve().with_name("phase12_final_candidate_config.json")
    package_path = Path(__file__).resolve().parents[1] / "configs" / "phase12_final_candidate_config.json"
    return sibling if sibling.exists() else package_path


def _load_candidate_config(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("hidden_2026_used") or config.get("uses_2025_for_tuning"):
        raise ValueError("Submission agent refuses a config with hidden 2026 or 2025 tuning.")
    candidate = dict(config["candidates"][FINAL_CANDIDATE_ID])
    if normalize_track(str(candidate.get("track"))) != FINAL_TRACK:
        raise ValueError("B2_real config track mismatch.")
    for key in PATH_KEYS:
        value = candidate.get(key)
        if value and not Path(str(value)).is_absolute():
            candidate[key] = str(PACKAGE_ROOT / str(value))
    return candidate


class TrackBB2RealSubmissionAgent:
    """Official-compatible, fixed-policy Track B submission agent."""

    def __init__(
        self,
        *,
        track: str = FINAL_TRACK,
        trace_dir: str | Path | None = None,
        config_path: str | Path | None = None,
        ablation_type: str = "active_real_tensor",
    ) -> None:
        if normalize_track(track) != FINAL_TRACK:
            raise ValueError("TrackBB2RealSubmissionAgent only supports sector/Track B.")
        self.track = FINAL_TRACK
        self.candidate_id = FINAL_CANDIDATE_ID
        self.trace_dir = Path(trace_dir) if trace_dir is not None else PACKAGE_ROOT / "runtime_logs" / "track_b_b2_submission_traces"
        self.config_path = Path(config_path) if config_path is not None else _default_config_path()
        self.candidate_config = _load_candidate_config(self.config_path)
        self.agent = Prompt09RealTransformerAgent(
            track=self.track,
            candidate_id=self.candidate_id,
            trace_dir=self.trace_dir,
            candidate_config=self.candidate_config,
            ablation_type=ablation_type,
        )

    def decide(self, **kwargs: Any) -> dict[str, Any]:
        requested_track = kwargs.get("track")
        if requested_track is not None and normalize_track(str(requested_track)) != FINAL_TRACK:
            raise ValueError("TrackBB2RealSubmissionAgent rejects a non-Track-B decision request.")
        return self.agent.decide(**kwargs)

    async def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        final_decision = self.decide(**kwargs)
        await asyncio.sleep(0)
        return {"final_decision": final_decision}


def build_agent(**kwargs: Any) -> TrackBB2RealSubmissionAgent:
    """Official-style factory for an explicitly Track B submission package."""

    return TrackBB2RealSubmissionAgent(**kwargs)
