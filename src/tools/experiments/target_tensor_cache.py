"""Persistent cache for generated target-weight tensors."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np


@dataclass(frozen=True)
class TargetTensorBundle:
    dates: tuple[str, ...]
    assets: tuple[str, ...]
    candidate_names: tuple[str, ...]
    open_prices: np.ndarray
    pct_changes: np.ndarray
    target_weights: np.ndarray
    metadata: dict[str, Any]


class TargetTensorCache:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def key_for(self, payload: Mapping[str, Any]) -> str:
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def paths_for(self, key: str) -> tuple[Path, Path]:
        directory = self.root / key[:2]
        return directory / f"{key}.npz", directory / f"{key}.json"

    def exists(self, key: str) -> bool:
        npz_path, meta_path = self.paths_for(key)
        return npz_path.exists() and meta_path.exists()

    def save(self, key: str, bundle: TargetTensorBundle) -> tuple[Path, Path]:
        npz_path, meta_path = self.paths_for(key)
        npz_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            npz_path,
            dates=np.asarray(bundle.dates),
            assets=np.asarray(bundle.assets),
            candidate_names=np.asarray(bundle.candidate_names),
            open_prices=bundle.open_prices,
            pct_changes=bundle.pct_changes,
            target_weights=bundle.target_weights,
        )
        metadata = dict(bundle.metadata)
        metadata["cache_key"] = key
        metadata["npz_path"] = str(npz_path)
        meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")
        return npz_path, meta_path

    def load(self, key: str) -> TargetTensorBundle:
        npz_path, meta_path = self.paths_for(key)
        arrays = np.load(npz_path, allow_pickle=False)
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        return TargetTensorBundle(
            dates=tuple(str(item) for item in arrays["dates"].tolist()),
            assets=tuple(str(item) for item in arrays["assets"].tolist()),
            candidate_names=tuple(str(item) for item in arrays["candidate_names"].tolist()),
            open_prices=arrays["open_prices"],
            pct_changes=arrays["pct_changes"],
            target_weights=arrays["target_weights"],
            metadata=metadata,
        )


def tensor_fingerprint(bundle: TargetTensorBundle) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(bundle.target_weights).tobytes())
    digest.update(json.dumps(bundle.candidate_names, sort_keys=True).encode("utf-8"))
    digest.update(json.dumps(bundle.dates, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()
