"""Financial tone. Lexicon baseline + optional local transformer (FinBERT-style).

The lexicon below is a small hand-written list (not Loughran-McDonald; the LM
dictionary can be loaded with :meth:`LexiconSentiment.from_word_lists` from a
local copy if its terms permit your use).
"""

from __future__ import annotations

import math
import os
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from icaif.nlp.embeddings import EncoderSpec, ModelUnavailable

POSITIVE = frozenset(["beat", "beats", "exceeded", "exceed", "raise", "raises", "raised", "record", "strong", "stronger", "growth", "accelerate", "accelerates", "accelerating", "upgrade", "upgrades", "upgraded", "outperform", "buyback", "dividend", "expansion", "surge", "surges", "soared", "rally", "gain", "gains", "approval", "approved", "wins", "win", "profit", "profitable", "rebound", "robust", "boost", "boosts", "optimistic"])
NEGATIVE = frozenset(["miss", "misses", "missed", "cut", "cuts", "lowered", "lower", "weak", "weaker", "weakens", "decline", "declines", "fell", "falls", "drop", "drops", "downgrade", "downgrades", "downgraded", "underperform", "loss", "losses", "lawsuit", "probe", "investigation", "recall", "halt", "halts", "layoffs", "warning", "warns", "slump", "plunge", "plunges", "delay", "delays", "fine", "fined", "bankruptcy", "default", "costs", "pressure", "slowing", "slows"])
NEGATORS = frozenset(["not", "no", "never", "without", "fails", "failed", "n't"])


@dataclass(frozen=True)
class SentimentResult:
    score: float  # [-1, 1]
    confidence: float  # [0, 1]
    probabilities: tuple[float, float, float]  # (neg, neu, pos)
    model_id: str


def entropy_confidence(p: Sequence[float]) -> float:
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1.0)
    h = -float(np.sum(p * np.log(p)))
    return float(1.0 - h / math.log(len(p)))


class LexiconSentiment:
    model_id = "lexicon_tone_v1"

    def __init__(self, positive: Iterable[str] = POSITIVE, negative: Iterable[str] = NEGATIVE) -> None:
        self.positive, self.negative = frozenset(positive), frozenset(negative)

    @classmethod
    def from_word_lists(cls, positive_path: Path, negative_path: Path) -> LexiconSentiment:
        read = lambda p: {w.strip().lower() for w in Path(p).read_text(encoding="utf-8").split() if w.strip()}  # noqa: E731
        return cls(read(positive_path), read(negative_path))

    def score(self, text: str) -> SentimentResult:
        tokens = re.findall(r"[a-z']+", text.lower())
        pos = neg = 0
        for i, tok in enumerate(tokens):
            flip = any(t in NEGATORS for t in tokens[max(0, i - 3):i])
            if tok in self.positive:
                pos, neg = (pos, neg + 1) if flip else (pos + 1, neg)
            elif tok in self.negative:
                pos, neg = (pos + 1, neg) if flip else (pos, neg + 1)
        hits = pos + neg
        if hits == 0:
            return SentimentResult(0.0, 0.0, (0.0, 1.0, 0.0), self.model_id)
        score = (pos - neg) / hits
        conf = min(0.9, 0.3 + 0.15 * hits) * abs(score)
        p_pos = (1 + score) / 2 * conf
        p_neg = (1 - score) / 2 * conf
        return SentimentResult(float(score), float(conf), (p_neg, 1 - p_pos - p_neg, p_pos), self.model_id)


class LocalTransformerSentiment:
    """Local sequence classifier with labels containing pos/neg/neu (e.g. ProsusAI/finbert).

    Never downloads; raises ModelUnavailable when files/deps are missing.
    """

    def __init__(self, spec: EncoderSpec, *, device: str = "cpu", max_length: int = 256) -> None:
        self.model_id = spec.model_id
        if not spec.local_path or not Path(os.path.expanduser(spec.local_path)).exists():
            raise ModelUnavailable(f"{spec.model_id}: local model not found")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        try:
            import torch  # type: ignore[import-not-found]
            from transformers import (  # type: ignore[import-not-found]
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )
        except ImportError as error:
            raise ModelUnavailable("transformers/torch not installed (pip install '.[nlp]')") from error
        path = os.path.expanduser(spec.local_path)
        self._torch = torch
        self._tok = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self._model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True).to(device).eval()
        self._device = device
        self._max_length = max_length
        labels = {int(k): str(v).lower() for k, v in self._model.config.id2label.items()}
        try:
            self._idx = tuple(next(i for i, lab in labels.items() if key in lab) for key in ("neg", "neu", "pos"))
        except StopIteration as error:
            raise ModelUnavailable(f"{spec.model_id}: labels {labels} lack neg/neu/pos") from error

    def score(self, text: str) -> SentimentResult:
        enc = self._tok([text], truncation=True, max_length=self._max_length, return_tensors="pt").to(self._device)
        with self._torch.no_grad():
            probs = self._torch.softmax(self._model(**enc).logits, dim=-1)[0].cpu().numpy()
        p = tuple(float(probs[i]) for i in self._idx)
        return SentimentResult(p[2] - p[0], entropy_confidence(p), p, self.model_id)  # type: ignore[arg-type]
