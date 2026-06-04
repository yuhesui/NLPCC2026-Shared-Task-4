"""CPU/GPU device selection for the News Overlay scaffold."""

from __future__ import annotations

from importlib.util import find_spec


def resolve_device(requested: str = "auto") -> str:
    """Resolve a device string without importing heavy ML libraries unless present."""

    normalized = (requested or "auto").lower()
    if normalized == "cpu":
        return "cpu"
    if normalized == "cuda":
        return "cuda" if _cuda_available() else "cpu"
    if normalized != "auto":
        raise ValueError(f"Unsupported device: {requested!r}")
    return "cuda" if _cuda_available() else "cpu"


def _cuda_available() -> bool:
    if find_spec("torch") is None:
        return False
    try:
        import torch  # type: ignore

        return bool(torch.cuda.is_available())
    except Exception:
        return False
