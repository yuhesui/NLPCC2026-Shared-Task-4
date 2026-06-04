"""Local transformer feature-provider scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from nlpcc.news_overlay.base import AvailabilityStatus, MethodRunContext, MethodRunResult, ModelAvailabilityReport
from nlpcc.news_overlay.model_availability import check_model_availability
from nlpcc.news_overlay.registry import get_method_spec


@dataclass(frozen=True)
class OfflineTransformerFeatureProvider:
    """No-download feature provider used by smoke tests and future model adapters."""

    context: MethodRunContext

    def check_availability(self, method_code: str) -> ModelAvailabilityReport:
        return check_model_availability(get_method_spec(method_code), self.context)

    def encode_texts(self, texts: tuple[str, ...], *, method_code: str) -> MethodRunResult:
        spec = get_method_spec(method_code)
        report = self.check_availability(method_code)
        if report.status != AvailabilityStatus.AVAILABLE:
            return MethodRunResult(
                method_code=method_code,
                kind=spec.kind,
                status=report.status,
                fallback_code=spec.fallback_code,
                transformer_used=spec.transformer_used,
                network_attempted=False,
                outputs={},
                diagnostics={"availability": report.as_dict(), "text_count": len(texts)},
            )
        # Real inference is intentionally out of scope for this scaffold.
        return MethodRunResult(
            method_code=method_code,
            kind=spec.kind,
            status=AvailabilityStatus.AVAILABLE,
            transformer_used=spec.transformer_used,
            network_attempted=False,
            outputs={"embedding_count": len(texts), "embedding_dim": 0},
            diagnostics={"availability": report.as_dict(), "stub": True},
        )
