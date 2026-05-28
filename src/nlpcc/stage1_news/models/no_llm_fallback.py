"""No-LLM neutral fallback output."""

from __future__ import annotations

from nlpcc.stage1_news.schema import Stage1Config, Stage1Output


def no_llm_fallback_output(reason: str, config: Stage1Config | None = None) -> Stage1Output:
    cfg = config or Stage1Config()
    return Stage1Output(
        items=(),
        sentiments=(),
        events=(),
        sector_impacts=(),
        bl_views=(),
        fallback_used=True,
        diagnostics={
            "fallback_reason": reason,
            "fallback_confidence": cfg.fallback_confidence,
            "model": "no_llm_fallback",
        },
    )
