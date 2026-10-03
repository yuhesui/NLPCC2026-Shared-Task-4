"""Text encoders behind one interface, with a strict no-download policy.

* :class:`HashingEncoder` — deterministic bag-of-ngrams feature hashing. It
  is a *lexical baseline*, labelled as such everywhere; it is never presented
  as a transformer (AlphaAllocator's hash fallback was silently used as an
  "encoder proxy" — that is not repeated here).
* :class:`LocalSentenceEncoder` — sentence-transformers model loaded from a
  local directory only (``HF_HUB_OFFLINE=1``, ``local_files_only``). Missing
  model or dependency raises :class:`ModelUnavailable`; callers degrade
  explicitly and the trace records ``blocked_missing_local_model``.

Model *policy* lives in ``configs/embeddings/registry.yaml``: each entry has
``requires_rule_confirmation`` and ``status``; :func:`check_policy` refuses
models whose competition status is unconfirmed unless explicitly allowed for
offline research.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np


class ModelUnavailable(RuntimeError):
    """Local model files or optional dependency missing (status: blocked_missing_local_model)."""


class ModelPolicyError(RuntimeError):
    """Model use not permitted in this context (e.g. unconfirmed competition status in live mode)."""


@dataclass(frozen=True)
class EncoderSpec:
    model_id: str
    family: str
    local_path: str | None = None
    revision: str | None = None
    requires_rule_confirmation: bool = True
    status: str = "candidate"  # ready | requires_confirmation | unsuitable | deferred | baseline
    license: str = ""
    trained_through: str | None = None  # set for models fine-tuned in this repo
    notes: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> EncoderSpec:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def check_policy(spec: EncoderSpec, *, live: bool, allow_unconfirmed_research: bool = False) -> None:
    if spec.status == "unsuitable":
        raise ModelPolicyError(f"{spec.model_id} is marked unsuitable")
    if spec.requires_rule_confirmation:
        if live:
            raise ModelPolicyError(f"{spec.model_id} requires organizer rule confirmation before live use")
        if not allow_unconfirmed_research:
            raise ModelPolicyError(f"{spec.model_id} requires rule confirmation; set allow_unconfirmed_research for offline study")


class Encoder(Protocol):
    model_id: str
    is_transformer: bool

    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class HashingEncoder:
    """L2-normalised hashed unigram+bigram counts (deterministic, no deps)."""

    is_transformer = False

    def __init__(self, dims: int = 512) -> None:
        self.dims = dims
        self.model_id = f"lexical_hash_{dims}"

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, text in enumerate(texts):
            tokens = re.findall(r"[a-z0-9]+", text.lower())
            grams = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:], strict=False)]
            for g in grams:
                h = int.from_bytes(hashlib.blake2b(g.encode(), digest_size=8).digest(), "little")
                out[i, h % self.dims] += 1.0 if (h >> 63) & 1 else -1.0
            norm = np.linalg.norm(out[i])
            if norm > 0:
                out[i] /= norm
        return out


class LocalSentenceEncoder:
    is_transformer = True

    def __init__(self, spec: EncoderSpec, *, device: str = "cpu", batch_size: int = 32) -> None:
        self.spec = spec
        self.model_id = spec.model_id
        if not spec.local_path:
            raise ModelUnavailable(f"{spec.model_id}: no local_path configured")
        path = Path(os.path.expandvars(os.path.expanduser(spec.local_path)))
        if not path.exists():
            raise ModelUnavailable(f"{spec.model_id}: local model directory not found ({path})")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
        except ImportError as error:
            raise ModelUnavailable("sentence-transformers not installed (pip install '.[nlp]')") from error
        self._model = SentenceTransformer(str(path), device=device, local_files_only=True)
        self.batch_size = batch_size

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        vectors = self._model.encode(list(texts), batch_size=self.batch_size, normalize_embeddings=True,
                                     show_progress_bar=False, convert_to_numpy=True)
        return np.asarray(vectors, dtype=np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    an = a / np.maximum(np.linalg.norm(a, axis=-1, keepdims=True), 1e-12)
    bn = b / np.maximum(np.linalg.norm(b, axis=-1, keepdims=True), 1e-12)
    return an @ bn.T
