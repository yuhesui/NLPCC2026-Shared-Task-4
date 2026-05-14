"""Track 1 bounded macro-regime labels and deterministic mappings."""

TRACK1_REGIMES: tuple[str, ...] = (
    "risk_on",
    "risk_off",
    "policy_easing",
    "growth_slowdown",
    "inflation_commodity",
    "sector_policy_positive",
    "uncertain",
)

REGIME_GROUP_WEIGHTS: dict[str, dict[str, float]] = {
    "risk_on": {"equity": 0.72, "growth": 0.18, "commodity": 0.05, "defensive": 0.05},
    "risk_off": {"equity": 0.20, "growth": 0.05, "commodity": 0.15, "defensive": 0.60},
    "policy_easing": {"equity": 0.50, "growth": 0.28, "commodity": 0.05, "defensive": 0.17},
    "growth_slowdown": {"equity": 0.28, "growth": 0.07, "commodity": 0.10, "defensive": 0.55},
    "inflation_commodity": {"equity": 0.30, "growth": 0.05, "commodity": 0.40, "defensive": 0.25},
    "sector_policy_positive": {"equity": 0.42, "growth": 0.35, "commodity": 0.08, "defensive": 0.15},
    "uncertain": {"equity": 0.40, "growth": 0.10, "commodity": 0.10, "defensive": 0.40},
}
