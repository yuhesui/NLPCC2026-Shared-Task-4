"""Offline model availability checks with no silent downloads."""

from __future__ import annotations

from importlib.util import find_spec
import os
from pathlib import Path

from nlpcc.news_overlay.base import AvailabilityStatus, MethodRunContext, MethodSpec, ModelAvailabilityReport


PROXY_MODEL_REF = "proxy://shared-hash-encoder"
SHARED_ENCODER_PROXY_METHODS = frozenset({"N6"})
PROXY_ASSET_STATUSES = frozenset({"available_proxy_only", "available_via_shared_encoder"})


def model_ref_for_cache(spec: MethodSpec, context: MethodRunContext) -> str | None:
    """Return the model/cache identity used by local or proxy feature paths."""

    local_path = _configured_local_path(spec, context)
    if local_path:
        metadata = _configured_model_metadata(spec, context)
        hf_model_id = metadata.get("hf_model_id")
        revision = metadata.get("revision_or_commit") or metadata.get("revision")
        if hf_model_id or revision:
            return f"{hf_model_id or spec.model_identifier}@{revision or 'unknown'}:{local_path}"
        return local_path
    if context.proxy_mode and spec.local_model_required:
        return _proxy_model_ref(spec)
    return None


def is_proxy_report(report: ModelAvailabilityReport | dict[str, object]) -> bool:
    """Return true when an availability record represents explicit proxy execution."""

    if isinstance(report, ModelAvailabilityReport):
        return bool(report.proxy or report.asset_status in PROXY_ASSET_STATUSES)
    return bool(report.get("proxy") or report.get("asset_status") in PROXY_ASSET_STATUSES)


def composite_asset_status(component_results: list[object]) -> str:
    """Reduce component traces into one Prompt06.5 asset status."""

    statuses: list[str] = []
    for result in component_results:
        diagnostics = getattr(result, "diagnostics", {}) or {}
        availability = diagnostics.get("availability") or {}
        status = str(availability.get("asset_status") or availability.get("status") or getattr(result, "status", "not_applicable"))
        statuses.append(status)
    if any(status == "blocked_missing_dependency" for status in statuses):
        return "blocked_missing_dependency"
    if any(status == "blocked_missing_local_model" for status in statuses):
        return "blocked_missing_local_model"
    if any(status == "available_via_shared_encoder" for status in statuses):
        return "available_via_shared_encoder"
    if any(status == "available_proxy_only" for status in statuses):
        return "available_proxy_only"
    if statuses and all(status == "not_applicable" for status in statuses):
        return "not_applicable"
    return "available"


def check_model_availability(spec: MethodSpec, context: MethodRunContext) -> ModelAvailabilityReport:
    """Check local-only availability for one method.

    This function never downloads, opens network connections, or calls model
    libraries. It only verifies config, local path existence, and optional
    Python dependency visibility.
    """

    if spec.code in context.disabled_methods:
        metadata = _configured_model_metadata(spec, context)
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.DISABLED_BY_CONFIG,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="method_disabled_by_config",
            device=context.device,
            asset_status="disabled_by_config",
        )

    if not spec.local_model_required:
        metadata = _configured_model_metadata(spec, context)
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.AVAILABLE,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="no_local_model_required",
            device=context.device,
            asset_status="not_applicable",
        )

    if not context.offline:
        metadata = _configured_model_metadata(spec, context)
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_OFFLINE_POLICY,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="online_model_access_forbidden",
            device=context.device,
            asset_status="blocked_missing_local_model",
        )

    local_path = _configured_local_path(spec, context)
    metadata = _configured_model_metadata(spec, context)
    if context.proxy_mode and not local_path:
        asset_status = "available_via_shared_encoder" if spec.code in SHARED_ENCODER_PROXY_METHODS else "available_proxy_only"
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.AVAILABLE,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            local_path=_proxy_model_ref(spec),
            dependency=spec.dependency,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="proxy_mode_enabled_no_local_model",
            device=context.device,
            asset_status=asset_status,
            proxy=True,
            transformer_execution=False,
        )
    if not local_path:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="no_local_model_path_configured",
            device=context.device,
            asset_status="blocked_missing_local_model",
        )

    path = Path(local_path).expanduser()
    if not path.exists():
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            local_path=str(path),
            revision=metadata.get("revision_or_commit") or metadata.get("revision"),
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="local_model_path_missing",
            device=context.device,
            asset_status="blocked_missing_local_model",
        )

    if spec.dependency and find_spec(spec.dependency) is None:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_MISSING_DEPENDENCY,
            model_identifier=spec.model_identifier,
            hf_model_id=metadata.get("hf_model_id"),
            local_path=str(path),
            revision=metadata.get("revision_or_commit") or metadata.get("revision"),
            dependency=spec.dependency,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason=f"missing_dependency:{spec.dependency}",
            device=context.device,
            asset_status="blocked_missing_dependency",
        )

    return ModelAvailabilityReport(
        method_code=spec.code,
        status=AvailabilityStatus.AVAILABLE,
        model_identifier=spec.model_identifier,
        hf_model_id=metadata.get("hf_model_id"),
        local_path=str(path),
        revision=metadata.get("revision_or_commit") or metadata.get("revision"),
        dependency=spec.dependency,
        fallback_code=spec.fallback_code,
        network_attempted=False,
        local_files_only=True,
        reason="local_model_path_exists_local_files_only",
        device=context.device,
        asset_status="available",
        transformer_execution=True,
    )


def _proxy_model_ref(spec: MethodSpec) -> str:
    if spec.code in SHARED_ENCODER_PROXY_METHODS:
        return PROXY_MODEL_REF
    return f"proxy://{spec.model_identifier or spec.code.lower()}"


def _configured_local_path(spec: MethodSpec, context: MethodRunContext) -> str | None:
    explicit = context.local_model_paths.get(spec.code) or context.local_model_paths.get(spec.model_identifier or "")
    if explicit:
        return explicit
    if spec.model_identifier in {"bge_style_bi_encoder", "news_overlay_transformer_stack", "label_attention_event_tagger", "sector_query_attention_encoder"}:
        env_value = os.environ.get("BGE_MODEL_PATH")
        if env_value:
            return env_value
    if spec.model_identifier in {"finbert_style_aspect_tone", "aspect_impact_aggregator", "transformer_impact_stack"}:
        env_value = os.environ.get("FINBERT_MODEL_PATH") or os.environ.get("BGE_MODEL_PATH")
        if env_value:
            return env_value
    if spec.model_identifier == "cross_encoder_sector_reranker":
        env_value = os.environ.get("RERANKER_MODEL_PATH")
        if env_value:
            return env_value
    env_key = f"NEWS_OVERLAY_MODEL_{spec.code.upper()}"
    env_value = os.environ.get(env_key)
    if env_value:
        return env_value
    local_root = os.environ.get("NEWS_OVERLAY_LOCAL_MODELS")
    if local_root and spec.model_identifier:
        return str(Path(local_root) / spec.model_identifier)
    root = os.environ.get("NEWS_OVERLAY_MODEL_ROOT")
    if root and spec.model_identifier:
        return str(Path(root) / spec.model_identifier)
    hf_root = os.environ.get("NLPCC_HF_MODEL_DIR")
    if hf_root and spec.model_identifier:
        return str(Path(hf_root) / spec.model_identifier)
    return None


def _configured_model_metadata(spec: MethodSpec, context: MethodRunContext) -> dict[str, str]:
    metadata = (
        context.local_model_metadata.get(spec.code)
        or context.local_model_metadata.get(spec.model_identifier or "")
        or {}
    )
    return {str(key): str(value) for key, value in metadata.items()}
