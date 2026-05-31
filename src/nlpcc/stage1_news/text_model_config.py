"""Configuration for optional offline Stage 1 text models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TextModelConfig:
    enabled: bool = False
    provider: str = "local_huggingface"
    model_name: str | None = None
    local_path: str | None = None
    revision: str | None = None
    offline_only: bool = True
    fallback: str = "rule_based"
    max_length: int = 256
    embedding_dims: int = 16

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "TextModelConfig":
        if not values:
            return cls()
        return cls(**{key: value for key, value in values.items() if key in cls.__dataclass_fields__})
