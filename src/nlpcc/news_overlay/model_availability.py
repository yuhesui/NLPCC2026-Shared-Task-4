"""Offline model availability checks with no silent downloads."""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path

from nlpcc.news_overlay.base import AvailabilityStatus, MethodRunContext, MethodSpec, ModelAvailabilityReport


def check_model_availability(spec: MethodSpec, context: MethodRunContext) -> ModelAvailabilityReport:
    """Check local-only availability for one method.

    This function never downloads, opens network connections, or calls model
    libraries. It only verifies config, local path existence, and optional
    Python dependency visibility.
    """

    if spec.code in context.disabled_methods:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.DISABLED_BY_CONFIG,
            model_identifier=spec.model_identifier,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="method_disabled_by_config",
            device=context.device,
        )

    if not spec.local_model_required:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.AVAILABLE,
            model_identifier=spec.model_identifier,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="no_local_model_required",
            device=context.device,
        )

    if not context.offline:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_OFFLINE_POLICY,
            model_identifier=spec.model_identifier,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="online_model_access_forbidden",
            device=context.device,
        )

    local_path = context.local_model_paths.get(spec.code) or context.local_model_paths.get(spec.model_identifier or "")
    if not local_path:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL,
            model_identifier=spec.model_identifier,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="no_local_model_path_configured",
            device=context.device,
        )

    path = Path(local_path).expanduser()
    if not path.exists():
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL,
            model_identifier=spec.model_identifier,
            local_path=str(path),
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason="local_model_path_missing",
            device=context.device,
        )

    if spec.dependency and find_spec(spec.dependency) is None:
        return ModelAvailabilityReport(
            method_code=spec.code,
            status=AvailabilityStatus.BLOCKED_MISSING_DEPENDENCY,
            model_identifier=spec.model_identifier,
            local_path=str(path),
            dependency=spec.dependency,
            fallback_code=spec.fallback_code,
            network_attempted=False,
            reason=f"missing_dependency:{spec.dependency}",
            device=context.device,
        )

    return ModelAvailabilityReport(
        method_code=spec.code,
        status=AvailabilityStatus.AVAILABLE,
        model_identifier=spec.model_identifier,
        local_path=str(path),
        revision=None,
        dependency=spec.dependency,
        fallback_code=spec.fallback_code,
        network_attempted=False,
        reason="local_model_path_exists",
        device=context.device,
    )
