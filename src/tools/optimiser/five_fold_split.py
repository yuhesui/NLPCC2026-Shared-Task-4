"""Chronological five-fold 80/20 split helpers for 2024-2025 research CV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FiveFoldSplit:
    fold: int
    train_chunks: tuple[int, ...]
    validation_chunk: int
    train_date_ranges: tuple[tuple[str, str], ...]
    validation_date_range: tuple[str, str]
    train_dates: tuple[str, ...]
    validation_dates: tuple[str, ...]
    label: str = "research cross-validation / robustness analysis"

    def as_dict(self) -> dict[str, object]:
        return {
            "fold": self.fold,
            "train_chunks": list(self.train_chunks),
            "validation_chunk": self.validation_chunk,
            "train_date_ranges": list(self.train_date_ranges),
            "validation_date_range": self.validation_date_range,
            "train_count": len(self.train_dates),
            "validation_count": len(self.validation_dates),
            "label": self.label,
        }


def make_five_fold_80_20_splits(dates: Iterable[str]) -> tuple[FiveFoldSplit, ...]:
    ordered = tuple(sorted(str(date) for date in dates))
    if len(ordered) < 5:
        raise ValueError("At least five dates are required for five-fold splitting.")
    chunks = _chronological_chunks(ordered, 5)
    splits: list[FiveFoldSplit] = []
    for validation_index, validation_dates in enumerate(chunks):
        train_chunks = tuple(index + 1 for index in range(5) if index != validation_index)
        train_dates = tuple(date for index, chunk in enumerate(chunks) if index != validation_index for date in chunk)
        train_ranges = tuple((chunks[index][0], chunks[index][-1]) for index in range(5) if index != validation_index)
        splits.append(
            FiveFoldSplit(
                fold=validation_index + 1,
                train_chunks=train_chunks,
                validation_chunk=validation_index + 1,
                train_date_ranges=train_ranges,
                validation_date_range=(validation_dates[0], validation_dates[-1]),
                train_dates=train_dates,
                validation_dates=validation_dates,
            )
        )
    return tuple(splits)


def load_combined_trading_dates(
    roots: Iterable[Path],
    *,
    anchor_asset: str = "000300.SH",
) -> tuple[str, ...]:
    dates: set[str] = set()
    for root in roots:
        path = root / "price_data" / f"{anchor_asset}.csv"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                value = str(row.get("date", "")).strip()
                if value:
                    dates.add(value)
    if not dates:
        raise RuntimeError("No trading dates found in the provided roots.")
    return tuple(sorted(dates))


def _chronological_chunks(dates: tuple[str, ...], count: int) -> tuple[tuple[str, ...], ...]:
    base, remainder = divmod(len(dates), count)
    chunks = []
    cursor = 0
    for index in range(count):
        size = base + (1 if index < remainder else 0)
        chunk = dates[cursor : cursor + size]
        if not chunk:
            raise ValueError("Cannot create empty chronological chunk.")
        chunks.append(chunk)
        cursor += size
    return tuple(chunks)
