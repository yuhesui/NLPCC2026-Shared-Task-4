"""Small helpers for locating local mirrored and smoke-test data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalDataCatalog:
    repo_root: Path = Path(".")

    @property
    def train_2024(self) -> Path:
        return self.repo_root / "data" / "train_2024"

    @property
    def public_a_2025(self) -> Path:
        return self.repo_root / "data" / "public_a_2025"

    @property
    def smoke_test(self) -> Path:
        return self.repo_root / "data" / "sample" / "smoke_test"

    def price_dir(self, split: str) -> Path:
        return self._split_root(split) / "price_data"

    def news_dir(self, split: str) -> Path:
        return self._split_root(split) / "news_data"

    def _split_root(self, split: str) -> Path:
        if split == "train_2024":
            return self.train_2024
        if split == "public_a_2025":
            return self.public_a_2025
        if split == "smoke_test":
            return self.smoke_test
        raise ValueError(f"Unsupported split: {split!r}")
