"""Base interfaces and schemas for the transformer-first News Overlay scaffold."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Protocol


TrackCode = Literal["A", "B"]
MethodKind = Literal["N", "I", "S"]


class AvailabilityStatus(str, Enum):
    """Runtime availability states for optional transformer methods."""

    AVAILABLE = "available"
    BLOCKED_MISSING_LOCAL_MODEL = "blocked_missing_local_model"
    BLOCKED_MISSING_DEPENDENCY = "blocked_missing_dependency"
    BLOCKED_OFFLINE_POLICY = "blocked_offline_policy"
    DISABLED_BY_CONFIG = "disabled_by_config"
    FALLBACK_USED = "fallback_used"


@dataclass(frozen=True)
class ModelRequirement:
    """Local model/dependency requirement for a method."""

    model_identifier: str | None = None
    local_path: str | None = None
    revision: str | None = None
    dependency: str | None = None
    required: bool = False


@dataclass(frozen=True)
class ModelAvailabilityReport:
    """Structured offline model availability report."""

    method_code: str
    status: AvailabilityStatus
    model_identifier: str | None = None
    local_path: str | None = None
    revision: str | None = None
    dependency: str | None = None
    fallback_code: str | None = None
    network_attempted: bool = False
    reason: str | None = None
    device: str = "cpu"

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class MethodSpec:
    """Registry metadata for one N/I/S method or composite."""

    code: str
    kind: MethodKind
    name: str
    required_status: str
    role: str
    transformer_used: bool = False
    control: bool = False
    fallback: bool = False
    baseline: bool = False
    local_model_required: bool = False
    cache_required: bool = False
    fallback_code: str | None = None
    components: tuple[str, ...] = ()
    supported_tracks: tuple[TrackCode, ...] = ("A", "B")
    model_identifier: str | None = None
    dependency: str | None = None

    @property
    def is_composite(self) -> bool:
        return bool(self.components)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MethodRunContext:
    """Minimal execution context shared by method stubs."""

    track: TrackCode
    decision_date: str | None = None
    offline: bool = True
    device: str = "cpu"
    cache_dir: str = ".var/news_overlay_prompt01_11/cache"
    local_model_paths: dict[str, str] = field(default_factory=dict)
    disabled_methods: frozenset[str] = field(default_factory=frozenset)
    preprocessing_version: str = "news_overlay_v1"
    feature_schema_version: str = "news_overlay_schema_v4"
    batch_size: int = 16


@dataclass(frozen=True)
class MethodRunResult:
    """Result emitted by scaffold methods."""

    method_code: str
    kind: MethodKind
    status: AvailabilityStatus
    fallback_code: str | None = None
    transformer_used: bool = False
    network_attempted: bool = False
    outputs: dict[str, Any] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def fallback_used(self) -> bool:
        return self.status == AvailabilityStatus.FALLBACK_USED or self.fallback_code is not None

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class CacheManifestWriter(Protocol):
    """Protocol for cache manifest writers."""

    def write_manifest(self, rows: list[dict[str, Any]], path: str | Path) -> Path:
        ...


class TraceWriter(Protocol):
    """Protocol for trace writers."""

    def write_trace(self, trace: dict[str, Any], path: str | Path) -> Path:
        ...


class TransformerFeatureProvider(Protocol):
    """Protocol for local transformer feature providers."""

    def check_availability(self, method_code: str) -> ModelAvailabilityReport:
        ...

    def encode_texts(self, texts: tuple[str, ...], *, method_code: str) -> MethodRunResult:
        ...


class BaseNewsOverlayMethod(ABC):
    """Dependency-light base class for N/I/S scaffold methods."""

    kind: MethodKind

    def __init__(self, spec: MethodSpec):
        self.spec = spec

    @abstractmethod
    def run(self, context: MethodRunContext, payload: dict[str, Any] | None = None) -> MethodRunResult:
        """Run the method or report a blocked/fallback state."""


class NewsAnalysisMethod(BaseNewsOverlayMethod):
    kind: MethodKind = "N"


class NewsImpactMethod(BaseNewsOverlayMethod):
    kind: MethodKind = "I"


class NewsSensitivityMethod(BaseNewsOverlayMethod):
    kind: MethodKind = "S"


class NewsOverlayPipeline(Protocol):
    """Protocol for N + I + S composition."""

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        ...
