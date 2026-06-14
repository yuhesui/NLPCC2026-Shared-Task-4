"""Prompt02 merged public 2024/2025 Type-C split helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypeCFold:
    fold_id: str
    split_method: str
    train_dates: tuple[str, ...]
    test_dates: tuple[str, ...]
    purge_gap_days: int = 1

    def manifest_row(self) -> dict[str, object]:
        total = len(self.train_dates) + len(self.test_dates)
        return {
            "fold_id": self.fold_id,
            "split_method": self.split_method,
            "train_start": self.train_dates[0],
            "train_end": self.train_dates[-1],
            "test_start": self.test_dates[0],
            "test_end": self.test_dates[-1],
            "train_days": len(self.train_dates),
            "test_days": len(self.test_dates),
            "train_pct": round(len(self.train_dates) / total, 6) if total else 0.0,
            "test_pct": round(len(self.test_dates) / total, 6) if total else 0.0,
            "purge_gap_days": self.purge_gap_days,
            "leakage_check_status": "pass_public_dates_no_same_day_overlap",
            "notes": "Type C research-only purged blocked split; no hidden 2026.",
        }


def build_purged_blocked_folds(dates: list[str], *, folds: int = 5, test_pct: float = 0.20, purge_gap_days: int = 1) -> list[TypeCFold]:
    """Build five contiguous held-out blocks with an 80/20 train/test ratio."""

    if folds <= 0:
        raise ValueError("folds must be positive.")
    unique_dates = sorted(dict.fromkeys(dates))
    if len(unique_dates) < folds * 2:
        raise ValueError("not enough dates for Type-C folds.")
    test_size = max(1, round(len(unique_dates) * test_pct))
    result: list[TypeCFold] = []
    max_start = max(0, len(unique_dates) - test_size)
    starts = [round(idx * max_start / max(1, folds - 1)) for idx in range(folds)]
    for idx, start in enumerate(starts, 1):
        stop = min(len(unique_dates), start + test_size)
        test_dates = tuple(unique_dates[start:stop])
        purge = set(unique_dates[max(0, start - purge_gap_days) : min(len(unique_dates), stop + purge_gap_days)])
        train_dates = tuple(date for date in unique_dates if date not in set(test_dates) and date not in purge)
        result.append(
            TypeCFold(
                fold_id=f"fold_{idx}",
                split_method="purged_blocked_80_20_research_only",
                train_dates=train_dates,
                test_dates=test_dates,
                purge_gap_days=purge_gap_days,
            )
        )
    return result
