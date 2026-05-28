"""Deterministic parameter search spaces."""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import random
from typing import Any, Iterable


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    values: tuple[Any, ...]


@dataclass(frozen=True)
class SearchSpace:
    parameters: tuple[ParameterSpec, ...]

    @classmethod
    def from_mapping(cls, mapping: dict[str, Iterable[Any]]) -> "SearchSpace":
        return cls(tuple(ParameterSpec(name, tuple(values)) for name, values in sorted(mapping.items())))

    def grid(self) -> list[dict[str, Any]]:
        names = [parameter.name for parameter in self.parameters]
        value_sets = [parameter.values for parameter in self.parameters]
        return [dict(zip(names, combo)) for combo in itertools.product(*value_sets)]

    def sample(self, count: int, seed: int = 0) -> list[dict[str, Any]]:
        rng = random.Random(seed)
        grid = self.grid()
        if count >= len(grid):
            return grid
        indexes = sorted(rng.sample(range(len(grid)), count))
        return [grid[index] for index in indexes]
