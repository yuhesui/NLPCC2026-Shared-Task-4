"""Organizer LLM policy (starter-kit docs/llm_and_external_data.md, 2026-09-21).

LLM use is optional; if used it must be one of the listed families and be
disclosed (model name, version, provider, prompts, inference settings, API
configuration). The list names *families*, not exact versions, so exact
model identifiers are configured explicitly and checked here by family.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ALLOWED_FAMILIES: dict[str, tuple[str, ...]] = {
    # open-weight
    "llama-4": (r"llama[-_ ]?4",),
    "qwen3": (r"qwen[-_ ]?3",),
    "deepseek-v3": (r"deepseek[-_ ]?v3",),
    "deepseek-r1": (r"deepseek[-_ ]?r1",),
    "gemma-3": (r"gemma[-_ ]?3",),
    "mistral-large": (r"mistral[-_ ]?large",),
    # hosted
    "gpt-5": (r"^gpt[-_ ]?5$", r"^gpt[-_ ]?5[-_](?!mini)"),
    "gpt-5-mini": (r"gpt[-_ ]?5[-_ ]?mini",),
    "claude-opus-5": (r"claude[-_ ]?opus[-_ ]?5",),
    "claude-sonnet-5": (r"claude[-_ ]?sonnet[-_ ]?5",),
    "claude-haiku-4.5": (r"claude[-_ ]?haiku[-_ ]?4[-_.]5",),
    "gemini-2.5-pro": (r"gemini[-_ ]?2\.5[-_ ]?pro",),
    "gemini-2.5-flash": (r"gemini[-_ ]?2\.5[-_ ]?flash",),
    "grok-4": (r"grok[-_ ]?4",),
}


class LLMPolicyError(RuntimeError):
    pass


@dataclass(frozen=True)
class PolicyCheck:
    model_id: str
    family: str | None
    allowed: bool
    note: str


def check_model(model_id: str) -> PolicyCheck:
    lowered = model_id.lower()
    for family, patterns in ALLOWED_FAMILIES.items():
        if any(re.search(p, lowered) for p in patterns):
            note = "family listed by organizer; confirm exact version is acceptable" if family in (
                "qwen3", "llama-4", "gemma-3") else "family listed by organizer"
            return PolicyCheck(model_id, family, True, note)
    return PolicyCheck(model_id, None, False, "not in organizer LLM list")


def assert_allowed(model_id: str) -> PolicyCheck:
    result = check_model(model_id)
    if not result.allowed:
        raise LLMPolicyError(f"LLM {model_id!r} is not an organizer-supported model")
    return result
