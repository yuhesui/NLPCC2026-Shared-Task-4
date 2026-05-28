"""Walk-forward split helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WalkForwardSplit:
    train_start: str
    train_end: str
    test_start: str
    test_end: str


def make_rolling_splits(dates: list[str], *, train_size: int, test_size: int, step_size: int | None = None) -> list[WalkForwardSplit]:
    step = step_size or test_size
    splits: list[WalkForwardSplit] = []
    start = 0
    while start + train_size + test_size <= len(dates):
        train = dates[start : start + train_size]
        test = dates[start + train_size : start + train_size + test_size]
        splits.append(WalkForwardSplit(train[0], train[-1], test[0], test[-1]))
        start += step
    return splits
