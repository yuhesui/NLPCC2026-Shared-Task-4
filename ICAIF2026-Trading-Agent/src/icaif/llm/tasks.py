"""Structured LLM tasks: extract_event, classify_relevance, estimate_impact,
summarize_evidence. LLMs act as information extractors whose outputs are
validated and bounded; they do not allocate capital in production.

``direct_allocation`` exists only as an experimental baseline (Q-LLM-ALLOC in
the experiment matrix) and is refused unless explicitly enabled.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from icaif.core.schemas import Article
from icaif.core.universe import SYMBOLS
from icaif.llm.client import LLMClient, LLMRequest
from icaif.nlp.event_extraction import EVENT_TYPES

SYSTEM = ("You are a financial information extractor. Use only the article text provided. "
          "Do not use knowledge of events after the article's publication time. Answer with JSON only.")


class LLMOutputError(ValueError):
    pass


def _parse_json(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise LLMOutputError("no JSON object in LLM output")
    try:
        value = json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        raise LLMOutputError(f"invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise LLMOutputError("LLM output must be a JSON object")
    return value


def _article_block(article: Article) -> str:
    return f"PUBLISHED_AT: {article.published_at.isoformat()}\nTITLE: {article.title}\nBODY: {article.body[:4000]}"


@dataclass(frozen=True)
class LLMEvent:
    ticker: str | None
    event_type: str
    direction: int
    magnitude: float
    confidence: float
    expected_horizon_hours: float
    evidence: str


def extract_event(client: LLMClient, article: Article) -> list[LLMEvent]:
    prompt = (f"{_article_block(article)}\n\nList material events. Allowed tickers: {', '.join(SYMBOLS)} or null for "
              f"market-wide. Allowed event_type: {', '.join(EVENT_TYPES)}. Return "
              '{"events":[{"ticker":..,"event_type":..,"direction":-1|0|1,"magnitude":0..1,"confidence":0..1,'
              '"expected_horizon_hours":number,"evidence":"short quote"}]}')
    data = _parse_json(client.complete(LLMRequest("extract_event", prompt, SYSTEM)).text)
    out = []
    for row in data.get("events", []):
        ticker = row.get("ticker")
        if ticker is not None and ticker not in SYMBOLS:
            continue  # unknown tickers are dropped, never mapped by guesswork
        etype = row.get("event_type")
        if etype not in EVENT_TYPES:
            continue
        try:
            direction = int(row.get("direction", 0))
            mag = float(row.get("magnitude", 0.0))
            conf = float(row.get("confidence", 0.0))
            horizon = float(row.get("expected_horizon_hours", 13.0))
        except (TypeError, ValueError):
            continue
        if direction not in (-1, 0, 1):
            continue
        out.append(LLMEvent(ticker, etype, direction, min(max(mag, 0.0), 1.0), min(max(conf, 0.0), 1.0),
                            min(max(horizon, 0.5), 24.0 * 30), str(row.get("evidence", ""))[:300]))
    return out


def classify_relevance(client: LLMClient, article: Article, ticker: str) -> tuple[float, float, str]:
    if ticker not in SYMBOLS:
        raise ValueError(f"unknown ticker {ticker}")
    prompt = (f"{_article_block(article)}\n\nHow directly does this article affect {ticker}'s stock? Return "
              '{"relevance":0..1,"confidence":0..1,"reason":"short"}')
    data = _parse_json(client.complete(LLMRequest("classify_relevance", prompt, SYSTEM)).text)
    try:
        rel = min(max(float(data["relevance"]), 0.0), 1.0)
        conf = min(max(float(data.get("confidence", 0.5)), 0.0), 1.0)
    except (KeyError, TypeError, ValueError) as error:
        raise LLMOutputError(f"bad relevance output: {error}") from error
    return rel, conf, str(data.get("reason", ""))[:300]


def estimate_impact(client: LLMClient, article: Article, ticker: str) -> tuple[int, float]:
    prompt = (f"{_article_block(article)}\n\nExpected direction of {ticker}'s idiosyncratic return over the next "
              'trading day. Return {"direction":-1|0|1,"confidence":0..1}')
    data = _parse_json(client.complete(LLMRequest("estimate_impact", prompt, SYSTEM)).text)
    direction = int(data.get("direction", 0))
    if direction not in (-1, 0, 1):
        raise LLMOutputError("direction out of range")
    return direction, min(max(float(data.get("confidence", 0.0)), 0.0), 1.0)


def summarize_evidence(client: LLMClient, articles: list[Article], ticker: str) -> str:
    joined = "\n---\n".join(_article_block(a) for a in articles[:8])
    prompt = f"{joined}\n\nSummarise in <= 60 words what these say about {ticker}. Return {{\"summary\":\"...\"}}"
    return str(_parse_json(client.complete(LLMRequest("summarize_evidence", prompt, SYSTEM)).text).get("summary", ""))[:600]


def direct_allocation(*_: Any, enabled: bool = False, **__: Any) -> None:
    if not enabled:
        raise PermissionError("direct LLM allocation is an experimental baseline only; enable explicitly in research")
    raise NotImplementedError("TODO(research): direct-allocation baseline; outputs must pass the same validators")
