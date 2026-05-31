"""Training-only cross-sectional rank labels."""

from __future__ import annotations

from typing import Any


def build_rank_training_labels(
    price_rows_by_fund: dict[str, list[dict[str, Any]]],
    *,
    horizon: int = 5,
) -> dict[int, dict[str, int]]:
    """Create future-return rank labels for 2024 tooling only.

    This helper is not called from runtime agents because it intentionally uses
    future rows relative to each label date.
    """

    common_dates = sorted(
        set.intersection(
            *[
                {int(str(row.get("date_int", row.get("date"))).replace("-", "")[:8]) for row in rows}
                for rows in price_rows_by_fund.values()
                if rows
            ]
        )
    )
    labels: dict[int, dict[str, int]] = {}
    for index, date_int in enumerate(common_dates):
        future_index = index + horizon
        if future_index >= len(common_dates):
            break
        scores: list[tuple[float, str]] = []
        for fund_id, rows in price_rows_by_fund.items():
            by_date = {int(str(row.get("date_int", row.get("date"))).replace("-", "")[:8]): row for row in rows}
            current = by_date.get(date_int)
            future = by_date.get(common_dates[future_index])
            if not current or not future:
                continue
            current_close = float(current.get("close") or 0.0)
            future_close = float(future.get("close") or 0.0)
            if current_close > 0 and future_close > 0:
                scores.append(((future_close / current_close) - 1.0, fund_id))
        scores.sort(reverse=True)
        labels[date_int] = {fund_id: rank + 1 for rank, (_, fund_id) in enumerate(scores)}
    return labels
