"""Experiment configuration objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    agent_name: str
    data_root: Path
    track: str = "macro"
    lookback_days: int = 60
    load_news: bool = False
    output_dir: Path = Path("outputs/experiments")
    agent_params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "ExperimentConfig":
        data = dict(values)
        data["data_root"] = Path(data["data_root"])
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])
        return cls(**data)
