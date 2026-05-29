"""Experiment configuration objects and deterministic hashing."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    agent_name: str
    data_root: Path
    track: str = "macro"
    lookback_days: int = 60
    max_dates: int | None = None
    load_news: bool = False
    news_lookback_calendar_days: int = 1
    initial_capital: float = 100000.0
    output_dir: Path = Path("outputs/experiments")
    agent_params: dict[str, Any] = field(default_factory=dict)
    ablation: str = "base"
    group: str = "default"
    notes: str = ""

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "ExperimentConfig":
        data = dict(values)
        data["data_root"] = Path(data["data_root"])
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})

    def to_mapping(self) -> dict[str, Any]:
        data = asdict(self)
        data["data_root"] = str(self.data_root)
        data["output_dir"] = str(self.output_dir)
        return data

    def config_hash(self) -> str:
        payload = json.dumps(self.to_mapping(), sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @property
    def run_id(self) -> str:
        return f"{self.name}_{self.config_hash()}"


@dataclass(frozen=True)
class ExperimentSuiteConfig:
    name: str
    experiments: tuple[ExperimentConfig, ...]
    report_dir: Path = Path("outputs/reports")

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "ExperimentSuiteConfig":
        data = dict(values)
        defaults = dict(data.pop("defaults", {}) or {})
        output_dir = Path(defaults.get("output_dir", "outputs/experiments"))
        experiments = []
        for item in data.pop("experiments", []) or []:
            merged = {**defaults, **item}
            merged.setdefault("output_dir", output_dir)
            experiments.append(ExperimentConfig.from_mapping(merged))
        report_dir = Path(data.pop("report_dir", "outputs/reports"))
        return cls(
            name=str(data.pop("name")),
            experiments=tuple(experiments),
            report_dir=report_dir,
        )
