"""Offline BGE-small Chinese embedding extractor for Stage 1."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any

from nlpcc.stage1_news.local_model_loader import LocalModelUnavailable, load_encoder_model, resolve_local_model_path
from nlpcc.stage1_news.schema import NormalizedNewsItem
from nlpcc.stage1_news.text_model_config import TextModelConfig


DEFAULT_BGE_MODEL = "BAAI/bge-small-zh-v1.5"


@dataclass(frozen=True)
class EmbeddingSignal:
    news_id: str
    embedding_ref: str
    vector_preview: tuple[float, ...]
    relevance_score: float
    model_metadata: dict[str, Any]


def deterministic_text_embedding(text: str, *, dims: int = 16) -> tuple[float, ...]:
    """Small deterministic fallback embedding used when no local model is enabled."""

    digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
    values: list[float] = []
    for idx in range(max(1, dims)):
        byte = digest[idx % len(digest)]
        values.append(round((byte / 127.5) - 1.0, 6))
    norm = sum(value * value for value in values) ** 0.5 or 1.0
    return tuple(round(value / norm, 6) for value in values)


@dataclass(frozen=True)
class BgeSmallZhEmbeddingExtractor:
    config: TextModelConfig = TextModelConfig(
        enabled=True,
        model_name=DEFAULT_BGE_MODEL,
        fallback="rule_based",
    )

    def resolve_path(self) -> str:
        return str(resolve_local_model_path(self.config.model_name or DEFAULT_BGE_MODEL, self.config.local_path))

    def embed_items(self, items: tuple[NormalizedNewsItem, ...]) -> tuple[EmbeddingSignal, ...]:
        model_name = self.config.model_name or DEFAULT_BGE_MODEL
        try:
            tokenizer, model, model_dir = load_encoder_model(model_name, self.config.local_path, self.config.max_length)
            vectors = self._model_embeddings(tokenizer, model, [item.text for item in items])
            fallback_used = False
            path_source = str(model_dir)
        except LocalModelUnavailable as exc:
            if self.config.fallback != "rule_based":
                raise
            vectors = [deterministic_text_embedding(item.text, dims=self.config.embedding_dims) for item in items]
            fallback_used = True
            path_source = f"fallback:{exc}"

        signals: list[EmbeddingSignal] = []
        for item, vector in zip(items, vectors):
            compact = tuple(round(float(value), 6) for value in vector[: max(1, self.config.embedding_dims)])
            vector_blob = ",".join(f"{value:.6f}" for value in compact)
            ref = hashlib.sha256(f"{item.news_id}:{vector_blob}".encode("utf-8")).hexdigest()[:16]
            relevance = min(1.0, 0.30 + 0.04 * len(item.text[:400].split()))
            signals.append(
                EmbeddingSignal(
                    news_id=item.news_id,
                    embedding_ref=f"bge:{ref}",
                    vector_preview=compact,
                    relevance_score=round(relevance, 6),
                    model_metadata={
                        "model": model_name,
                        "local_path_source": path_source,
                        "offline_only": self.config.offline_only,
                        "fallback_used": fallback_used,
                    },
                )
            )
        return tuple(signals)

    def _model_embeddings(self, tokenizer: Any, model: Any, texts: list[str]) -> list[tuple[float, ...]]:
        if not texts:
            return []
        try:
            import torch  # type: ignore
        except ModuleNotFoundError as exc:
            raise LocalModelUnavailable("torch is required for local embedding models") from exc
        encoded = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=int(self.config.max_length),
            return_tensors="pt",
        )
        with torch.no_grad():
            output = model(**encoded)
            hidden = output.last_hidden_state
            mask = encoded["attention_mask"].unsqueeze(-1).expand(hidden.size()).float()
            pooled = torch.sum(hidden * mask, dim=1) / torch.clamp(mask.sum(dim=1), min=1e-9)
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
        return [tuple(float(value) for value in row.tolist()) for row in pooled]
