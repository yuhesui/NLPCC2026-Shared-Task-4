"""Controlled optional LLM extractor.

Tests and default execution never require an external API. A caller may inject
an offline callable that returns a Stage1Output; otherwise this class falls
back to the deterministic no-LLM path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from nlpcc.stage1_news.models.no_llm_fallback import no_llm_fallback_output
from nlpcc.stage1_news.schema import NormalizedNewsItem, Stage1Config, Stage1Output


LLMCallable = Callable[[tuple[NormalizedNewsItem, ...]], Stage1Output]


@dataclass(frozen=True)
class ControlledLLMEventExtractor:
    config: Stage1Config = Stage1Config()
    offline_callable: LLMCallable | None = None

    def extract(self, items: tuple[NormalizedNewsItem, ...]) -> Stage1Output:
        if not self.config.use_llm or self.offline_callable is None:
            return no_llm_fallback_output("llm_disabled_or_unavailable", self.config)
        try:
            return self.offline_callable(items)
        except Exception as exc:
            return no_llm_fallback_output(f"llm_extractor_failed:{type(exc).__name__}", self.config)
