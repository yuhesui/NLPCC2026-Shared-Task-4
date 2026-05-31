"""Offline Hugging Face model path discovery and lazy loading."""

from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from typing import Any


class LocalModelUnavailable(RuntimeError):
    """Raised when an optional local model is not present on disk."""


def sanitize_model_name(model_name: str) -> str:
    return model_name.replace("/", "--")


def resolve_local_model_path(model_name: str, local_path: str | None = None) -> Path:
    """Resolve an already-downloaded Hugging Face model without network access."""

    candidates: list[Path] = []
    if local_path:
        candidates.append(Path(local_path).expanduser())

    env_root = os.environ.get("NLPCC_HF_MODEL_DIR")
    if env_root:
        root = Path(env_root).expanduser()
        candidates.extend(
            (
                root / model_name,
                root / sanitize_model_name(model_name),
                root / f"models--{sanitize_model_name(model_name)}",
            )
        )

    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")).expanduser()
    candidates.append(hf_home / "hub" / f"models--{sanitize_model_name(model_name)}")

    for candidate in candidates:
        resolved = _snapshot_or_model_dir(candidate)
        if resolved is not None:
            return resolved

    checked = ", ".join(str(path) for path in candidates)
    raise LocalModelUnavailable(
        f"Local model '{model_name}' was not found. Checked: {checked}. "
        f"Download it before offline use with: hf download {model_name}"
    )


def _snapshot_or_model_dir(path: Path) -> Path | None:
    if not path.exists():
        return None
    if (path / "config.json").exists():
        return path
    snapshots = path / "snapshots"
    if snapshots.exists():
        for snapshot in sorted(snapshots.iterdir(), reverse=True):
            if snapshot.is_dir() and (snapshot / "config.json").exists():
                return snapshot
    return None


@lru_cache(maxsize=4)
def load_sequence_classifier(model_name: str, local_path: str | None, max_length: int) -> tuple[Any, Any, Any]:
    del max_length
    model_dir = resolve_local_model_path(model_name, local_path)
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
    except ModuleNotFoundError as exc:
        raise LocalModelUnavailable("transformers is required for local sentiment models") from exc
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir), local_files_only=True)
    model.eval()
    return tokenizer, model, model_dir


@lru_cache(maxsize=4)
def load_encoder_model(model_name: str, local_path: str | None, max_length: int) -> tuple[Any, Any, Any]:
    del max_length
    model_dir = resolve_local_model_path(model_name, local_path)
    try:
        from transformers import AutoModel, AutoTokenizer  # type: ignore
    except ModuleNotFoundError as exc:
        raise LocalModelUnavailable("transformers is required for local embedding models") from exc
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
    model = AutoModel.from_pretrained(str(model_dir), local_files_only=True)
    model.eval()
    return tokenizer, model, model_dir
