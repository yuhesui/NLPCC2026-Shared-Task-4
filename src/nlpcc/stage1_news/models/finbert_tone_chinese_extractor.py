"""Offline FinBERT Chinese tone extractor for Stage 1."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from nlpcc.stage1_news.local_model_loader import LocalModelUnavailable, load_sequence_classifier, resolve_local_model_path
from nlpcc.stage1_news.models.sentiment_classifier import classify_sentiment
from nlpcc.stage1_news.schema import NormalizedNewsItem, SentimentSignal
from nlpcc.stage1_news.text_model_config import TextModelConfig


DEFAULT_FINBERT_MODEL = "yiyanghkust/finbert-tone-chinese"


@dataclass(frozen=True)
class FinbertToneChineseSentimentExtractor:
    config: TextModelConfig = TextModelConfig(
        enabled=True,
        model_name=DEFAULT_FINBERT_MODEL,
        fallback="rule_based",
    )

    def resolve_path(self) -> str:
        return str(resolve_local_model_path(self.config.model_name or DEFAULT_FINBERT_MODEL, self.config.local_path))

    def classify_items(self, items: tuple[NormalizedNewsItem, ...]) -> tuple[SentimentSignal, ...]:
        model_name = self.config.model_name or DEFAULT_FINBERT_MODEL
        try:
            tokenizer, model, model_dir = load_sequence_classifier(model_name, self.config.local_path, self.config.max_length)
            return self._model_sentiments(tokenizer, model, items, model_name=model_name, path_source=str(model_dir))
        except LocalModelUnavailable as exc:
            if self.config.fallback != "rule_based":
                raise
            return tuple(
                replace(
                    classify_sentiment(item),
                    model_name=model_name,
                    model_metadata={
                        "fallback_used": True,
                        "fallback_reason": str(exc),
                        "offline_only": self.config.offline_only,
                    },
                )
                for item in items
            )

    def _model_sentiments(
        self,
        tokenizer: Any,
        model: Any,
        items: tuple[NormalizedNewsItem, ...],
        *,
        model_name: str,
        path_source: str,
    ) -> tuple[SentimentSignal, ...]:
        if not items:
            return ()
        try:
            import torch  # type: ignore
        except ModuleNotFoundError as exc:
            raise LocalModelUnavailable("torch is required for local sentiment models") from exc
        texts = [item.text for item in items]
        encoded = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=int(self.config.max_length),
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = model(**encoded).logits
            probabilities = torch.softmax(logits, dim=-1)
        id2label = getattr(model.config, "id2label", {}) or {}
        output: list[SentimentSignal] = []
        for item, probs in zip(items, probabilities):
            score_values = [float(value) for value in probs.tolist()]
            best_idx = max(range(len(score_values)), key=lambda idx: score_values[idx])
            label = _canonical_label(str(id2label.get(best_idx, id2label.get(str(best_idx), best_idx))), best_idx)
            signed = _signed_score(label, score_values)
            output.append(
                SentimentSignal(
                    news_id=item.news_id,
                    label=label,
                    score=round(signed, 6),
                    confidence=round(score_values[best_idx], 6),
                    evidence=(f"finbert_label:{label}",),
                    model_name=model_name,
                    model_metadata={
                        "model": model_name,
                        "local_path_source": path_source,
                        "offline_only": self.config.offline_only,
                        "fallback_used": False,
                        "probabilities": [round(value, 6) for value in score_values],
                    },
                )
            )
        return tuple(output)


def _canonical_label(label: str, index: int) -> str:
    lowered = label.lower()
    if "positive" in lowered or "pos" == lowered or "积极" in lowered:
        return "positive"
    if "negative" in lowered or "neg" == lowered or "消极" in lowered:
        return "negative"
    if "neutral" in lowered or "neu" == lowered or "中性" in lowered:
        return "neutral"
    return {0: "neutral", 1: "positive", 2: "negative"}.get(index, "neutral")


def _signed_score(label: str, probabilities: list[float]) -> float:
    if len(probabilities) >= 3:
        return max(-1.0, min(1.0, probabilities[1] - probabilities[2]))
    if label == "positive":
        return probabilities[0]
    if label == "negative":
        return -probabilities[0]
    return 0.0
