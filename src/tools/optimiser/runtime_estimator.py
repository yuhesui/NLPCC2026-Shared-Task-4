"""Runtime estimation helpers for bounded grid-search planning."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeEstimate:
    scenario: str
    candidates: int
    dates: int
    folds: int
    backend: str
    hf_mode: str
    estimated_seconds: float

    @property
    def feasible_overnight(self) -> bool:
        return self.estimated_seconds <= 12 * 60 * 60

    def as_dict(self) -> dict[str, object]:
        return {
            "scenario": self.scenario,
            "candidates": self.candidates,
            "dates": self.dates,
            "folds": self.folds,
            "backend": self.backend,
            "hf_mode": self.hf_mode,
            "estimated_seconds": self.estimated_seconds,
            "feasible_overnight": self.feasible_overnight,
        }


def estimate_runtime_seconds(
    *,
    sample_seconds: float,
    sample_candidates: int,
    sample_dates: int,
    target_candidates: int,
    target_dates: int,
    folds: int = 1,
    hf_multiplier: float = 1.0,
    overhead_seconds: float = 0.0,
) -> float:
    if sample_seconds < 0 or sample_candidates <= 0 or sample_dates <= 0:
        raise ValueError("sample_seconds must be non-negative and sample sizes must be positive.")
    unit = sample_seconds / (sample_candidates * sample_dates)
    return overhead_seconds + unit * target_candidates * target_dates * max(1, folds) * max(1.0, hf_multiplier)


def make_runtime_estimate(
    *,
    scenario: str,
    sample_seconds: float,
    sample_candidates: int,
    sample_dates: int,
    candidates: int,
    dates: int,
    folds: int,
    backend: str,
    hf_mode: str,
    hf_multiplier: float = 1.0,
) -> RuntimeEstimate:
    return RuntimeEstimate(
        scenario=scenario,
        candidates=candidates,
        dates=dates,
        folds=folds,
        backend=backend,
        hf_mode=hf_mode,
        estimated_seconds=estimate_runtime_seconds(
            sample_seconds=sample_seconds,
            sample_candidates=sample_candidates,
            sample_dates=sample_dates,
            target_candidates=candidates,
            target_dates=dates,
            folds=folds,
            hf_multiplier=hf_multiplier,
        ),
    )
