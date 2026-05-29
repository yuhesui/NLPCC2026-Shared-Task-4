"""Runtime dependency checks for production-safe agents."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec


@dataclass(frozen=True)
class DependencyCheck:
    name: str
    available: bool
    required: bool = True
    reason: str | None = None

    def as_dict(self) -> dict[str, str | bool | None]:
        return {
            "name": self.name,
            "available": self.available,
            "required": self.required,
            "reason": self.reason,
        }


def check_python_dependencies(required: tuple[str, ...] = (), optional: tuple[str, ...] = ()) -> tuple[DependencyCheck, ...]:
    checks: list[DependencyCheck] = []
    for name in required:
        available = find_spec(name) is not None
        checks.append(
            DependencyCheck(
                name=name,
                available=available,
                required=True,
                reason=None if available else "missing_required_dependency",
            )
        )
    for name in optional:
        available = find_spec(name) is not None
        checks.append(
            DependencyCheck(
                name=name,
                available=available,
                required=False,
                reason=None if available else "missing_optional_dependency",
            )
        )
    return tuple(checks)


def missing_required_dependencies(required: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(check.name for check in check_python_dependencies(required=required) if check.required and not check.available)
