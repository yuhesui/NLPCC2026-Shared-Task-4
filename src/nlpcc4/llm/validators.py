"""Validation helpers for bounded LLM signals."""


def validate_confidence(confidence: float) -> None:
    """Validate normalized confidence values."""
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be in [0, 1]")
