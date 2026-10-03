"""Experiment registry: deterministic IDs, machine-readable records, evidence grades.

experiment_id = <family>.<name>.<10-hex digest of (config hash, dataset
manifest hash, seed, periods)> — rerunning the same experiment on the same
data yields the same id (and the registry refuses a *different* result under
an existing id). No "final_v2_fixed_REAL.csv" files: every artifact lives
under ``outputs/experiments/<experiment_id>/``.

``evidence_grade``:
  synthetic_plumbing   run on synthetic data — proves code paths only
  invalid_costs        fee override used — never evidence
  historical_backtest  point-in-time backtest on real historical data
  live_validation      organizer Validation phase results
"""

from __future__ import annotations

import csv
import json
import subprocess
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from icaif.core.config import REPO_ROOT, config_hash
from icaif.core.schemas import content_hash
from icaif.core.time import utc_now

DEFAULT_ROOT = REPO_ROOT / "outputs" / "experiments"
INDEX_FIELDS = ("experiment_id", "family", "name", "evidence_grade", "dataset", "config_hash", "seed",
                "validation_period", "cumulative_return", "sharpe_ratio", "maximum_drawdown", "turnover",
                "git_commit", "created_at")


def git_state(root: Path = REPO_ROOT) -> tuple[str, bool]:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=root, capture_output=True, text=True,
                                    check=True).stdout.strip())
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True


@dataclass
class ExperimentRecord:
    family: str
    name: str
    config: dict[str, Any]
    dataset_manifest: dict[str, Any]
    training_period: list[str] | None
    validation_period: list[str]
    seed: int
    metrics: dict[str, Any]
    summary: dict[str, Any] = field(default_factory=dict)
    features_used: list[str] = field(default_factory=list)
    text_sources: list[str] = field(default_factory=list)
    market_sources: list[str] = field(default_factory=list)
    artifact_paths: dict[str, str] = field(default_factory=dict)
    notes: str = ""
    evidence_grade: str = "synthetic_plumbing"
    git_commit: str = ""
    git_dirty: bool = True
    created_at: str = field(default_factory=lambda: utc_now().isoformat())

    @property
    def config_hash(self) -> str:
        return config_hash(self.config)

    @property
    def experiment_id(self) -> str:
        digest = content_hash([self.config_hash, self.dataset_manifest.get("manifest_hash"), self.seed,
                               self.training_period, self.validation_period])[:10]
        return f"{self.family}.{self.name}.{digest}"

    def as_dict(self) -> dict[str, Any]:
        body = asdict(self)
        body["experiment_id"] = self.experiment_id
        body["config_hash"] = self.config_hash
        return body


def grade(dataset_manifest: Mapping[str, Any], *, fee_overridden: bool, live: bool = False) -> str:
    if fee_overridden:
        return "invalid_costs"
    if dataset_manifest.get("synthetic", True):
        return "synthetic_plumbing"
    return "live_validation" if live else "historical_backtest"


class DuplicateExperimentError(RuntimeError):
    pass


class ExperimentRegistry:
    def __init__(self, root: Path = DEFAULT_ROOT) -> None:
        self.root = Path(root)

    def path_for(self, experiment_id: str) -> Path:
        return self.root / experiment_id

    def register(self, record: ExperimentRecord, *, overwrite: bool = False) -> Path:
        if not record.git_commit:
            record.git_commit, record.git_dirty = git_state()
        eid = record.experiment_id
        directory = self.path_for(eid)
        path = directory / "record.json"
        body = record.as_dict()
        if path.exists() and not overwrite:
            old = json.loads(path.read_text(encoding="utf-8"))
            if old.get("metrics") != json.loads(json.dumps(body["metrics"])):
                raise DuplicateExperimentError(f"{eid} exists with different metrics (non-determinism or changed code?)")
            return path
        directory.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(body, indent=2, sort_keys=True, default=str), encoding="utf-8")
        self._append_index(body)
        return path

    def _append_index(self, body: Mapping[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        index = self.root / "index.csv"
        new = not index.exists()
        m = body.get("metrics", {})
        row = {
            "experiment_id": body["experiment_id"], "family": body["family"], "name": body["name"],
            "evidence_grade": body["evidence_grade"], "dataset": body["dataset_manifest"].get("name"),
            "config_hash": body["config_hash"], "seed": body["seed"],
            "validation_period": "/".join(body["validation_period"]),
            **{k: m.get(k) for k in ("cumulative_return", "sharpe_ratio", "maximum_drawdown", "turnover")},
            "git_commit": body["git_commit"], "created_at": body["created_at"],
        }
        with index.open("a", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=INDEX_FIELDS)
            if new:
                writer.writeheader()
            writer.writerow(row)

    def load_all(self) -> list[dict[str, Any]]:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.root.glob("*/record.json"))]
