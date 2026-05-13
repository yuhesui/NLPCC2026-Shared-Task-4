"""Turnover metric utilities."""


def average_turnover(turnover_series: list[float]) -> float:
    """Return average turnover for a precomputed turnover series."""
    if not turnover_series:
        return 0.0
    return sum(turnover_series) / len(turnover_series)
