"""Validation helpers for market and news inputs."""


def validate_non_empty_fund_pool(fund_pool: tuple[str, ...]) -> None:
    """Validate that a strategy has at least one candidate fund."""
    if not fund_pool:
        raise ValueError("fund_pool must not be empty")
