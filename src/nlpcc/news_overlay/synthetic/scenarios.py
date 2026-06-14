"""Bounded synthetic scenarios from public 2024/2025 inputs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticScenario:
    name: str
    news_multiplier: float = 1.0
    price_noise: float = 0.0
    sharpe_shift: float = 0.0
    turnover_multiplier: float = 1.0
    notes: str = "research-only synthetic perturbation"


SCENARIOS: tuple[SyntheticScenario, ...] = (
    SyntheticScenario("news_drop_20pct", news_multiplier=0.80, sharpe_shift=-0.015),
    SyntheticScenario("news_drop_50pct", news_multiplier=0.50, sharpe_shift=-0.040),
    SyntheticScenario("news_duplicate_burst", news_multiplier=1.35, sharpe_shift=-0.025, turnover_multiplier=1.05),
    SyntheticScenario("news_sentiment_flip_small", sharpe_shift=-0.070),
    SyntheticScenario("sector_label_noise_10pct", sharpe_shift=-0.045),
    SyntheticScenario("event_intensity_scale_up", news_multiplier=1.15, sharpe_shift=0.020, turnover_multiplier=1.05),
    SyntheticScenario("event_intensity_scale_down", news_multiplier=0.85, sharpe_shift=-0.020),
    SyntheticScenario("price_noise_low", price_noise=0.003, sharpe_shift=-0.020),
    SyntheticScenario("price_noise_medium", price_noise=0.008, sharpe_shift=-0.060, turnover_multiplier=1.08),
    SyntheticScenario("crash_block_replay", price_noise=0.015, sharpe_shift=-0.180, turnover_multiplier=1.10),
    SyntheticScenario("volatility_regime_shuffle", price_noise=0.010, sharpe_shift=-0.085, turnover_multiplier=1.06),
    SyntheticScenario("turnover_cost_double", sharpe_shift=-0.035, turnover_multiplier=2.0),
)
