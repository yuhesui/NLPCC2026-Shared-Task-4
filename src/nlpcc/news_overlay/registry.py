"""Method registry for transformer-first News Overlay N/I/S methods."""

from __future__ import annotations

from collections.abc import Iterable

from nlpcc.news_overlay.base import (
    AvailabilityStatus,
    BaseNewsOverlayMethod,
    MethodRunContext,
    MethodRunResult,
    MethodSpec,
    NewsAnalysisMethod,
    NewsImpactMethod,
    NewsSensitivityMethod,
    TrackCode,
)
from nlpcc.news_overlay.model_availability import check_model_availability
from nlpcc.news_overlay.i_methods.architectures import RealNewsImpactMethod
from nlpcc.news_overlay.n_methods.architectures import RealNewsAnalysisMethod
from nlpcc.news_overlay.s_methods.architectures import RealNewsSensitivityMethod


class NewsOverlayRegistryError(ValueError):
    """Raised when a method code or composition is invalid."""


class _ScaffoldMethodMixin(BaseNewsOverlayMethod):
    """Shared run behavior for dependency-light scaffold methods."""

    def run(self, context: MethodRunContext, payload: dict | None = None) -> MethodRunResult:
        del payload
        if context.track not in self.spec.supported_tracks:
            raise NewsOverlayRegistryError(f"{self.spec.code} is not compatible with Track {context.track}")
        report = check_model_availability(self.spec, context)
        diagnostics = {
            "availability": report.as_dict(),
            "control": self.spec.control,
            "fallback": self.spec.fallback,
            "baseline": self.spec.baseline,
            "components": self.spec.components,
        }
        if report.status == AvailabilityStatus.AVAILABLE:
            return MethodRunResult(
                method_code=self.spec.code,
                kind=self.spec.kind,
                status=AvailabilityStatus.AVAILABLE,
                fallback_code=None,
                transformer_used=self.spec.transformer_used,
                network_attempted=False,
                outputs={"stub_feature": f"{self.spec.code}:available"},
                diagnostics=diagnostics,
            )
        return MethodRunResult(
            method_code=self.spec.code,
            kind=self.spec.kind,
            status=report.status,
            fallback_code=self.spec.fallback_code,
            transformer_used=self.spec.transformer_used,
            network_attempted=False,
            outputs={},
            diagnostics=diagnostics,
        )


class ScaffoldNewsAnalysisMethod(_ScaffoldMethodMixin, NewsAnalysisMethod):
    pass


class ScaffoldNewsImpactMethod(_ScaffoldMethodMixin, NewsImpactMethod):
    pass


class ScaffoldNewsSensitivityMethod(_ScaffoldMethodMixin, NewsSensitivityMethod):
    pass


METHOD_SPECS: dict[str, MethodSpec] = {
    "N0": MethodSpec("N0", "N", "no-news/base-only control", "control", "base/null", control=True),
    "N1": MethodSpec(
        "N1",
        "N",
        "deterministic taxonomy + entity/BM25 relevance",
        "fallback/baseline",
        "lexical baseline only",
        fallback=True,
        baseline=True,
    ),
    "N2": MethodSpec(
        "N2",
        "N",
        "BGE-style or sentence-transformer bi-encoder relevance cache",
        "required",
        "main transformer relevance method",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        model_identifier="bge_style_bi_encoder",
        dependency="transformers",
    ),
    "N3": MethodSpec(
        "N3",
        "N",
        "frozen FinBERT-style aspect-tone classifier",
        "required",
        "contextual tone/aspect feature",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        model_identifier="finbert_style_aspect_tone",
        dependency="transformers",
    ),
    "N4": MethodSpec(
        "N4",
        "N",
        "label-attention / Title2Event-inspired event tagger",
        "required",
        "transformer event typing and argument extraction",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        model_identifier="label_attention_event_tagger",
        dependency="transformers",
    ),
    "N5": MethodSpec(
        "N5",
        "N",
        "sector-query attention daily news pooling",
        "required",
        "attention aggregation over daily Top-20 news",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        model_identifier="sector_query_attention_encoder",
        dependency="transformers",
    ),
    "N6": MethodSpec(
        "N6",
        "N",
        "cross-encoder sector reranker gate",
        "required_if_local_reranker_exists",
        "high-precision second-stage relevance",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N2",
        model_identifier="cross_encoder_sector_reranker",
        dependency="transformers",
    ),
    "N7": MethodSpec(
        "N7",
        "N",
        "temporal lagged-news attention encoder",
        "required_lightweight",
        "narrative persistence over lagged news",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        model_identifier="temporal_lagged_news_attention",
        dependency="transformers",
    ),
    "N8": MethodSpec(
        "N8",
        "N",
        "entity-sector graph-attention propagation",
        "ablation/defer",
        "indirect sector relevance",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        model_identifier="entity_sector_graph_attention",
        dependency="transformers",
    ),
    "N12": MethodSpec(
        "N12",
        "N",
        "N1 + N2 lexical/embedding hybrid",
        "required",
        "robust hybrid relevance",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        components=("N1", "N2"),
        model_identifier="bge_style_bi_encoder",
        dependency="transformers",
    ),
    "N13": MethodSpec(
        "N13",
        "N",
        "N1 + N3 lexical/aspect-tone hybrid",
        "required",
        "robust hybrid tone",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        components=("N1", "N3"),
        model_identifier="finbert_style_aspect_tone",
        dependency="transformers",
    ),
    "N2345": MethodSpec(
        "N2345",
        "N",
        "N2 + N3 + N4 + N5 transformer-stack",
        "required",
        "primary transformer-first stack",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="N1",
        components=("N2", "N3", "N4", "N5"),
        model_identifier="news_overlay_transformer_stack",
        dependency="transformers",
    ),
    "I0": MethodSpec("I0", "I", "zero-impact control", "control", "null", control=True),
    "I1": MethodSpec(
        "I1", "I", "deterministic event magnitude score", "fallback/baseline", "baseline only", fallback=True, baseline=True
    ),
    "I2": MethodSpec("I2", "I", "Permutation-Tested News Attention Index", "required", "transparent index", cache_required=True),
    "I3": MethodSpec("I3", "I", "event-study calibrated impact score", "required", "CAR/CAAR impact calibration", cache_required=True),
    "I4": MethodSpec("I4", "I", "decay-weighted event persistence", "required", "persistence and novelty control", cache_required=True),
    "I5": MethodSpec(
        "I5",
        "I",
        "impact-gated attention pooling",
        "required",
        "attention impact aggregation",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="I1",
        model_identifier="impact_attention_pooler",
        dependency="transformers",
    ),
    "I6": MethodSpec(
        "I6",
        "I",
        "transformer aspect-impact aggregator",
        "required",
        "FinBERT/aspect-aware impact score",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="I1",
        model_identifier="aspect_impact_aggregator",
        dependency="transformers",
    ),
    "I7": MethodSpec(
        "I7",
        "I",
        "temporal narrative impact encoder",
        "required_lightweight",
        "lagged narrative impact",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="I4",
        model_identifier="temporal_narrative_impact_encoder",
        dependency="transformers",
    ),
    "I23": MethodSpec(
        "I23",
        "I",
        "I2 + I3 NAI plus event-study impact",
        "required",
        "robust impact core",
        cache_required=True,
        components=("I2", "I3"),
    ),
    "I256": MethodSpec(
        "I256",
        "I",
        "I2 + I5 + I6 transformer-impact stack",
        "required",
        "primary transformer-impact stack",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="I23",
        components=("I2", "I5", "I6"),
        model_identifier="transformer_impact_stack",
        dependency="transformers",
    ),
    "S0": MethodSpec("S0", "S", "no-sensitivity / uniform control", "control", "null", control=True),
    "S1": MethodSpec("S1", "S", "CAR/CAAR event-study sensitivity matrix", "required", "event-class sensitivity", cache_required=True),
    "S2": MethodSpec(
        "S2", "S", "Rank-IC Gated Sector News Momentum", "required", "Track B signal validation", cache_required=True, supported_tracks=("B",)
    ),
    "S3": MethodSpec(
        "S3", "S", "Volatility-Scaled Macro News Risk Gate", "required", "Track A risk gate", cache_required=True, supported_tracks=("A",)
    ),
    "S4": MethodSpec("S4", "S", "Sparse Event-Sensitivity Regression Overlay", "required", "data-driven sensitivity", cache_required=True),
    "S5": MethodSpec("S5", "S", "Black-Litterman News View Overlay", "recommended", "Bayesian view overlay", cache_required=True),
    "S6": MethodSpec(
        "S6",
        "S",
        "attention-weighted asset sensitivity pooling",
        "required",
        "transformer/attention sensitivity",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="S1",
        model_identifier="attention_weighted_sensitivity_pooler",
        dependency="transformers",
    ),
    "S7": MethodSpec(
        "S7",
        "S",
        "cross-sectional transformer score-to-tilt gate",
        "ablation/research",
        "learned score-to-overlay",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="S1",
        model_identifier="cross_sectional_score_to_tilt",
        dependency="transformers",
    ),
    "S12": MethodSpec(
        "S12",
        "S",
        "S1 + S2 event-study sensitivity + Rank-IC",
        "required",
        "Track B first robust gate",
        cache_required=True,
        components=("S1", "S2"),
        supported_tracks=("B",),
    ),
    "S13": MethodSpec(
        "S13",
        "S",
        "S1 + S3 event-study sensitivity + macro risk",
        "required",
        "Track A first robust gate",
        cache_required=True,
        components=("S1", "S3"),
        supported_tracks=("A",),
    ),
    "S126": MethodSpec(
        "S126",
        "S",
        "S1 + S2 + S6 transformer-aware sector gate",
        "required",
        "primary Track B transformer-aware gate",
        transformer_used=True,
        local_model_required=True,
        cache_required=True,
        fallback_code="S12",
        components=("S1", "S2", "S6"),
        supported_tracks=("B",),
        model_identifier="transformer_aware_sector_gate",
        dependency="transformers",
    ),
}


def list_method_specs(kind: str | None = None) -> tuple[MethodSpec, ...]:
    specs = tuple(METHOD_SPECS[code] for code in sorted(METHOD_SPECS))
    if kind is None:
        return specs
    normalized = kind.upper()
    return tuple(spec for spec in specs if spec.kind == normalized)


def get_method_spec(code: str) -> MethodSpec:
    normalized = code.upper()
    try:
        return METHOD_SPECS[normalized]
    except KeyError as exc:
        raise NewsOverlayRegistryError(f"Unknown News Overlay method code: {code!r}") from exc


def resolve_composite(code: str) -> tuple[MethodSpec, ...]:
    spec = get_method_spec(code)
    if not spec.components:
        return (spec,)
    return tuple(get_method_spec(component) for component in spec.components)


def validate_track_compatibility(track: TrackCode, codes: Iterable[str]) -> None:
    for code in codes:
        spec = get_method_spec(code)
        if track not in spec.supported_tracks:
            raise NewsOverlayRegistryError(f"{spec.code} is not compatible with Track {track}")


def instantiate_method(code: str) -> BaseNewsOverlayMethod:
    spec = get_method_spec(code)
    if spec.kind == "N":
        return RealNewsAnalysisMethod(spec)
    if spec.kind == "I":
        return RealNewsImpactMethod(spec)
    if spec.kind == "S":
        return RealNewsSensitivityMethod(spec)
    raise NewsOverlayRegistryError(f"Unsupported method kind for {code!r}: {spec.kind!r}")


def method_status_rows(context: MethodRunContext) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec in list_method_specs():
        report = check_model_availability(spec, context)
        row = spec.as_dict()
        row.update(
            {
                "status": report.status.value,
                "fallback_code": spec.fallback_code,
                "network_attempted": report.network_attempted,
                "availability_reason": report.reason,
            }
        )
        rows.append(row)
    return rows
