"""Structured schemas for bounded LLM signals."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmSignal:
    """Minimal parsed LLM signal contract."""

    label: str
    confidence: float
    rationale: str = ""
