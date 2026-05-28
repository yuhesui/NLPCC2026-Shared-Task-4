"""Optional CUDA capability checks.

The project must remain CPU-runnable. CUDA is therefore an optional capability
reported for experiments, never a hard dependency.
"""

from __future__ import annotations

import importlib.util
import os


def is_cuda_available() -> bool:
    if os.environ.get("CUDA_VISIBLE_DEVICES") in {"", "-1"}:
        return False
    if importlib.util.find_spec("torch") is None:
        return False
    try:
        import torch  # type: ignore
    except Exception:
        return False
    return bool(torch.cuda.is_available())


def describe_cuda_status() -> dict[str, object]:
    torch_available = importlib.util.find_spec("torch") is not None
    available = is_cuda_available()
    return {
        "available": available,
        "torch_available": torch_available,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "reason": "available" if available else "CUDA is unavailable or disabled; CPU path should be used.",
    }
