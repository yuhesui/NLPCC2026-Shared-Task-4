"""Fallback helpers for invalid or low-confidence signals."""


def fallback_to_s1() -> None:
    """Select S1 fallback once S1 implementation exists."""
    raise NotImplementedError("Fallback selection is planned.")
