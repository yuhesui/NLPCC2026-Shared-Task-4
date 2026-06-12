"""Substage N transformer-first news architecture implementations."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, time
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from typing import Any

from nlpcc.news_overlay.base import (
    AvailabilityStatus,
    MethodRunContext,
    MethodRunResult,
    MethodSpec,
    ModelAvailabilityReport,
    NewsAnalysisMethod,
)
from nlpcc.news_overlay.cache import build_cache_key
from nlpcc.news_overlay.model_availability import (
    check_model_availability,
    composite_asset_status,
    is_proxy_report,
    model_ref_for_cache,
)
from nlpcc.stage1_news.pipeline import filter_visible_news, normalize_news_items
from nlpcc.stage1_news.schema import NormalizedNewsItem


ASPECTS = ("policy", "regulation", "demand", "liquidity", "earnings", "geopolitics", "risk")

_LOCAL_MODEL_CACHE: dict[tuple[str, str, str], tuple[Any, Any]] = {}

SECTOR_PROTOTYPES: dict[str, tuple[str, ...]] = {
    "bank": ("银行", "商业银行", "息差", "信贷", "降准", "流动性", "512800", "bank"),
    "brokerage": ("券商", "证券", "资本市场", "交易活跃", "512880", "brokerage"),
    "insurance": ("保险", "保费", "权益投资", "512070", "insurance"),
    "semiconductor": ("半导体", "芯片", "集成电路", "国产替代", "159995", "semiconductor"),
    "ai": ("人工智能", "算力", "大模型", "AI", "159819", "ai"),
    "communication": ("通信", "5G", "光模块", "通信设备", "515880", "communication"),
    "software": ("软件", "信创", "云计算", "159852", "software"),
    "pharma": ("医药", "药品", "集采", "512010", "pharma"),
    "healthcare": ("医疗", "器械", "医疗服务", "512170", "healthcare"),
    "innovative_drug": ("创新药", "临床", "CXO", "159992", "innovative drug"),
    "food_beverage": ("食品饮料", "消费", "515170", "food beverage"),
    "liquor": ("白酒", "茅台", "酒企", "512690", "liquor"),
    "nonferrous": ("有色", "铜", "铝", "锂", "稀土", "512400", "nonferrous"),
    "coal": ("煤炭", "动力煤", "焦煤", "515220", "coal"),
    "chemicals": ("化工", "化学品", "农化", "159870", "chemicals"),
    "real_estate": ("房地产", "地产", "房企", "按揭", "512200", "real estate"),
    "broad_market": ("A股", "沪深300", "中证500", "创业板", "科创", "指数", "市场", "broad market"),
    "bond": ("债券", "国债", "利率", "收益率", "000012", "bond"),
    "gold": ("黄金", "金价", "避险", "518880", "gold"),
    "consumer": ("消费", "零售", "家电", "000932", "consumer"),
    "new_energy": ("新能源", "光伏", "锂电", "电动车", "000941", "new energy"),
    "media": ("传媒", "游戏", "影视", "399971", "media"),
    "energy": ("能源", "石油", "天然气", "000928", "energy"),
}

EVENT_LABELS: dict[str, str] = {
    "monetary_easing": "央行 降准 降息 流动性 货币 宽松 利率 下调",
    "liquidity_support": "释放 长期资金 流动性 融资 信贷 支持",
    "policy_support": "政策 支持 补贴 扶持 稳增长 国务院 发改委",
    "regulation_tightening": "监管 整顿 处罚 限制 规范 收紧",
    "demand_recovery": "需求 回暖 订单 增长 销量 复苏 景气",
    "earnings_growth": "盈利 利润 业绩 预增 收入 毛利",
    "geopolitical_risk": "地缘 冲突 制裁 关税 出口管制 海外",
    "default_credit_risk": "违约 债务 暴雷 展期 信用风险 房企",
    "commodity_supply": "供给 减产 库存 价格 上涨 大宗 商品",
    "tech_innovation": "AI 人工智能 芯片 算力 创新 国产替代",
    "healthcare_policy": "集采 医保 药品 医疗 政策 审批",
    "consumption_upgrade": "消费 白酒 食品饮料 旅游 零售 升级",
}

ASPECT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "policy": ("政策", "支持", "补贴", "国务院", "发改委", "财政"),
    "regulation": ("监管", "处罚", "整顿", "合规", "限制", "规范"),
    "demand": ("需求", "订单", "销量", "复苏", "回暖", "景气"),
    "liquidity": ("降准", "降息", "流动性", "融资", "信贷", "利率"),
    "earnings": ("盈利", "利润", "业绩", "预增", "收入", "毛利"),
    "geopolitics": ("地缘", "冲突", "制裁", "关税", "海外", "出口管制"),
    "risk": ("风险", "违约", "下滑", "亏损", "暴雷", "收紧"),
}

POSITIVE_CUES = ("利好", "支持", "增长", "上升", "改善", "释放", "回暖", "复苏", "预增", "宽松", "降准", "降息")
NEGATIVE_CUES = ("利空", "下滑", "下降", "亏损", "违约", "风险", "收紧", "处罚", "限制", "冲突", "制裁", "暴雷")
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


@dataclass(frozen=True)
class VisibleNewsBundle:
    decision_date: str
    cutoff: str
    items: tuple[NormalizedNewsItem, ...]
    diagnostics: dict[str, int]


class LocalTransformerLoadError(RuntimeError):
    """Raised when a configured local transformer cannot be loaded offline."""


class RealNewsAnalysisMethod(NewsAnalysisMethod):
    """Concrete Substage N implementation with cache and fallback support."""

    def run(self, context: MethodRunContext, payload: dict[str, Any] | None = None) -> MethodRunResult:
        if context.track not in self.spec.supported_tracks:
            raise ValueError(f"{self.spec.code} is not compatible with Track {context.track}")
        bundle = _visible_news_bundle(payload, context)
        cache_key = _method_cache_key(self.spec, context, bundle)
        cached = _read_cache(context, self.spec.code, cache_key)
        if cached is not None:
            cached["diagnostics"]["cache_hit"] = True
            return MethodRunResult(
                method_code=self.spec.code,
                kind="N",
                status=AvailabilityStatus(cached["status"]),
                fallback_code=cached.get("fallback_code"),
                transformer_used=bool(cached.get("transformer_used")),
                network_attempted=False,
                outputs=cached["outputs"],
                diagnostics=cached["diagnostics"],
            )

        runners = {
            "N0": _run_n0,
            "N1": _run_n1,
            "N2": _run_n2,
            "N3": _run_n3,
            "N4": _run_n4,
            "N5": _run_n5,
            "N7": _run_n7,
            "N8": _run_n8,
        }
        if self.spec.code == "N6":
            result = _run_unavailable_interface(self.spec, context, bundle, cache_key, fallback_code="N2")
        elif self.spec.code in {"N12", "N13", "N2345"}:
            result = _run_composite(self.spec, context, payload, bundle, cache_key)
        else:
            result = runners[self.spec.code](self.spec, context, bundle, cache_key, payload)
        _write_cache(context, self.spec.code, cache_key, result)
        return result


def _visible_news_bundle(payload: dict[str, Any] | None, context: MethodRunContext) -> VisibleNewsBundle:
    data = payload or {}
    raw_news = data.get("news") or data.get("raw_news") or ()
    decision_date = str(data.get("decision_date") or context.decision_date or "unknown")
    cutoff = str(data.get("cutoff") or "15:00")
    normalized = normalize_news_items(tuple(raw_news))
    visible, diagnostics = filter_visible_news(
        normalized,
        decision_date=None if decision_date == "unknown" else decision_date,
        top_rank=int(data.get("top_rank") or 20),
        cutoff=_parse_cutoff(cutoff),
    )
    return VisibleNewsBundle(decision_date=decision_date, cutoff=cutoff, items=visible, diagnostics=diagnostics)


def _parse_cutoff(value: str) -> time:
    try:
        hour, minute = (int(part) for part in value.split(":")[:2])
        return time(hour, minute)
    except (TypeError, ValueError):
        return time(15, 0)


def _method_cache_key(spec: MethodSpec, context: MethodRunContext, bundle: VisibleNewsBundle) -> str:
    texts = tuple(item.text for item in bundle.items)
    sources = tuple(item.source for item in bundle.items)
    local_path = model_ref_for_cache(spec, context)
    return build_cache_key(
        method_code=spec.code,
        model_identifier=spec.model_identifier,
        local_path_or_revision=local_path,
        preprocessing_version=context.preprocessing_version,
        texts=texts,
        date=bundle.decision_date,
        sources=sources,
        feature_schema_version=context.feature_schema_version,
    ).digest()


def _cache_path(context: MethodRunContext, method_code: str, cache_key: str) -> Path:
    return Path(context.cache_dir) / "n_methods" / method_code / f"{cache_key}.json"


def _read_cache(context: MethodRunContext, method_code: str, cache_key: str) -> dict[str, Any] | None:
    path = _cache_path(context, method_code, cache_key)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_cache(context: MethodRunContext, method_code: str, cache_key: str, result: MethodRunResult) -> None:
    path = _cache_path(context, method_code, cache_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "method_code": result.method_code,
        "status": result.status.value,
        "fallback_code": result.fallback_code,
        "transformer_used": result.transformer_used,
        "outputs": result.outputs,
        "diagnostics": {**result.diagnostics, "cache_hit": False},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _run_n0(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        bundle,
        cache_key,
        feature_rows=[],
        extra_outputs={"daily_features": {"relevance_by_sector": {}, "warnings": ("no_news_control",)}},
    )


def _run_n1(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    clusters = _duplicate_clusters(bundle.items)
    rows = []
    for item in bundle.items:
        event_probs = _label_scores(item.text, EVENT_LABELS)
        rows.append(
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                duplicate_cluster_id=clusters[item.news_id],
                relevance_by_sector=_lexical_relevance(item.text),
                aspect_tone=_aspect_tone(item.text),
                event_probabilities=event_probs,
                label_attention_scores=event_probs,
                entities=_extract_entities(item.text),
            )
        )
    return _result(spec, AvailabilityStatus.AVAILABLE, context, bundle, cache_key, feature_rows=rows, extra_outputs={"daily_features": _daily_summary(rows)})


def _run_n2(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    report = check_model_availability(spec, context)
    if report.status != AvailabilityStatus.AVAILABLE:
        rows = _fallback_rows(spec, context, bundle, cache_key, "N1")
        return _result(
            spec,
            report.status,
            context,
            bundle,
            cache_key,
            feature_rows=rows,
            fallback_code="N1",
            availability=report.as_dict(),
            extra_outputs={"daily_features": _daily_summary(rows), "embedding_backend": "fallback_lexical"},
        )
    if is_proxy_report(report):
        embeddings = [_hash_vector(item.text) for item in bundle.items]
        sector_embeddings = _hash_sector_vectors(32)
        embedding_backend = "proxy_hash_biencoder"
        row_warning = ("proxy_hash_biencoder",)
    else:
        try:
            embeddings = _encode_with_local_transformer(tuple(item.text for item in bundle.items), context, report.local_path)
            sector_names = tuple(SECTOR_PROTOTYPES)
            sector_texts = tuple(" ".join(SECTOR_PROTOTYPES[sector]) for sector in sector_names)
            encoded_sectors = _encode_with_local_transformer(sector_texts, context, report.local_path)
            sector_embeddings = dict(zip(sector_names, encoded_sectors))
            embedding_backend = "local_transformer_biencoder"
            row_warning = ("local_transformer_biencoder",)
        except LocalTransformerLoadError as exc:
            failed_report = _load_failure_report(report, exc)
            rows = _fallback_rows(spec, context, bundle, cache_key, "N1")
            return _result(
                spec,
                failed_report.status,
                context,
                bundle,
                cache_key,
                feature_rows=rows,
                fallback_code="N1",
                availability=failed_report.as_dict(),
                extra_outputs={"daily_features": _daily_summary(rows), "embedding_backend": "fallback_lexical", "model_error": str(exc)},
            )
    rows = []
    for item, vector in zip(bundle.items, embeddings):
        relevance = {sector: _cosine(vector, sector_vector) for sector, sector_vector in sector_embeddings.items()}
        rows.append(
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                relevance_by_sector=_top_scores(relevance),
                warnings=row_warning,
                extra={"embedding_backend": embedding_backend},
            )
        )
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        availability=report.as_dict(),
        extra_outputs={"daily_features": _daily_summary(rows), "embedding_backend": embedding_backend},
    )


def _run_n3(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    report = check_model_availability(spec, context)
    transformer_vectors: tuple[list[list[float]], dict[str, list[float]]] | None = None
    classifier_outputs: list[dict[str, Any]] | None = None
    if report.status == AvailabilityStatus.AVAILABLE:
        try:
            if is_proxy_report(report):
                text_vectors = [_hash_vector(item.text) for item in bundle.items]
                aspect_vectors = [_hash_vector(_aspect_description(aspect)) for aspect in ASPECTS]
                transformer_vectors = (text_vectors, dict(zip(ASPECTS, aspect_vectors)))
            elif _should_use_sequence_classifier(context, spec, report):
                classifier_outputs = _classify_with_local_sequence_classifier(
                    tuple(item.text for item in bundle.items),
                    context,
                    report.local_path,
                )
            else:
                text_vectors = _encode_with_local_transformer(tuple(item.text for item in bundle.items), context, report.local_path)
                aspect_vectors = _encode_with_local_transformer(tuple(_aspect_description(aspect) for aspect in ASPECTS), context, report.local_path)
                transformer_vectors = (text_vectors, dict(zip(ASPECTS, aspect_vectors)))
        except LocalTransformerLoadError as exc:
            report = _load_failure_report(report, exc)
    rows = []
    for item in bundle.items:
        aspect_tone = _aspect_tone(item.text)
        warnings = ("aspect_tone_fallback_used",)
        extra = {"aspect_tone_backend": "fallback_lexical_aspect_tone"}
        if classifier_outputs and report.status == AvailabilityStatus.AVAILABLE:
            classifier = classifier_outputs[len(rows)]
            aspect_tone = _aspect_tone_from_sentiment(item.text, float(classifier["sentiment_score"]))
            warnings = ("local_finbert_sequence_classifier",)
            extra = {
                "aspect_tone_backend": "local_sequence_classifier",
                "classifier_backend": "local_sequence_classifier",
                "classifier_probabilities": classifier["probabilities"],
                "classifier_label": classifier["label"],
                "sentiment_score": classifier["sentiment_score"],
            }
        elif transformer_vectors and report.status == AvailabilityStatus.AVAILABLE:
            text_vector = transformer_vectors[0][len(rows)]
            aspect_strength = {aspect: _cosine(text_vector, transformer_vectors[1][aspect]) for aspect in ASPECTS}
            aspect_tone = _scale_aspect_tone(aspect_tone, aspect_strength)
            if is_proxy_report(report):
                warnings = ("proxy_finbert_style_aspect_similarity",)
                backend = "proxy_hash_aspect_similarity"
            else:
                warnings = ("local_finbert_style_similarity",)
                backend = "local_transformer_similarity"
            extra = {"aspect_probabilities": _softmax_scores(aspect_strength), "aspect_tone_backend": backend}
        rows.append(
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                aspect_tone=aspect_tone,
                warnings=warnings,
                extra=extra,
            )
        )
    return _result(
        spec,
        report.status,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        fallback_code="N1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={"daily_features": _daily_summary(rows)},
    )


def _run_n4(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    report = check_model_availability(spec, context)
    text_vectors: list[list[float]] | None = None
    label_vectors: dict[str, list[float]] | None = None
    if report.status == AvailabilityStatus.AVAILABLE:
        try:
            labels = tuple(EVENT_LABELS)
            if is_proxy_report(report):
                text_vectors = [_hash_vector(item.text) for item in bundle.items]
                encoded_labels = [_hash_vector(f"{label}: {EVENT_LABELS[label]}") for label in labels]
            else:
                text_vectors = _encode_with_local_transformer(tuple(item.text for item in bundle.items), context, report.local_path)
                encoded_labels = _encode_with_local_transformer(tuple(f"{label}: {EVENT_LABELS[label]}" for label in labels), context, report.local_path)
            label_vectors = dict(zip(labels, encoded_labels))
        except LocalTransformerLoadError as exc:
            report = _load_failure_report(report, exc)
            text_vectors = None
            label_vectors = None
    rows = []
    for item in bundle.items:
        if text_vectors and label_vectors and report.status == AvailabilityStatus.AVAILABLE:
            raw_scores = {label: _cosine(text_vectors[len(rows)], vector) for label, vector in label_vectors.items()}
            label_scores = _softmax_scores(raw_scores)
            if is_proxy_report(report):
                warnings = ("proxy_label_attention_similarity",)
                backend = "proxy_hash_label_attention"
            else:
                warnings = ("local_label_attention_similarity",)
                backend = "local_transformer_similarity"
        else:
            label_scores = _label_scores(item.text, EVENT_LABELS)
            warnings = ("label_attention_fallback_used",)
            backend = "fallback_lexical_label_similarity"
        args = _event_arguments(item.text, label_scores)
        rows.append(
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                event_probabilities=label_scores,
                label_attention_scores=label_scores,
                entities=tuple(args["entities"]),
                relevance_by_sector=_lexical_relevance(item.text),
                aspect_tone=_aspect_tone(item.text),
                warnings=warnings,
                extra={
                    "event_arguments": args,
                    "label_attention_backend": backend,
                    "impact_side_fields": "lexical_relevance_and_aspect_tone",
                },
            )
        )
    return _result(
        spec,
        report.status,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        fallback_code="N1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={"daily_features": _daily_summary(rows)},
    )


def _run_n5(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    report = check_model_availability(spec, context)
    base_rows = []
    if report.status == AvailabilityStatus.AVAILABLE:
        try:
            sector_names = tuple(SECTOR_PROTOTYPES)
            if is_proxy_report(report):
                text_vectors = [_hash_vector(item.text) for item in bundle.items]
                sector_vectors = [_hash_vector(_sector_query_description(sector)) for sector in sector_names]
                row_warning = ("proxy_sector_query_attention",)
            else:
                text_vectors = _encode_with_local_transformer(tuple(item.text for item in bundle.items), context, report.local_path)
                sector_vectors = _encode_with_local_transformer(tuple(_sector_query_description(sector) for sector in sector_names), context, report.local_path)
                row_warning = ("local_sector_query_attention",)
            query_vectors = dict(zip(sector_names, sector_vectors))
            for item, vector in zip(bundle.items, text_vectors):
                relevance = {sector: _cosine(vector, query_vector) for sector, query_vector in query_vectors.items()}
                base_rows.append(
                    _row_with_scores(
                        spec,
                        context,
                        bundle,
                        item,
                        cache_key,
                        relevance_by_sector=_top_scores(relevance),
                        warnings=row_warning,
                    )
                )
        except LocalTransformerLoadError as exc:
            report = _load_failure_report(report, exc)
            base_rows = []
    if not base_rows:
        base_rows = [
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                relevance_by_sector=_lexical_relevance(item.text),
                warnings=("sector_query_attention_fallback_used",),
            )
            for item in bundle.items
        ]
    attention = _sector_attention(base_rows)
    rows = []
    for row in base_rows:
        news_id = row["news_id"]
        rows.append({**row, "sector_query_attention_weights": {sector: weights.get(news_id, 0.0) for sector, weights in attention.items()}})
    return _result(
        spec,
        report.status,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        fallback_code="N1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={
            "daily_features": _daily_summary(rows),
            "sector_attention": attention,
            "attention_backend": "proxy_hash_query_key"
            if is_proxy_report(report)
            else ("local_transformer_query_key" if report.status == AvailabilityStatus.AVAILABLE else "fallback_lexical_softmax"),
        },
    )


def _run_unavailable_interface(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    *,
    fallback_code: str,
) -> MethodRunResult:
    report = check_model_availability(spec, context)
    if report.status == AvailabilityStatus.AVAILABLE and is_proxy_report(report):
        sector_vectors = _hash_sector_vectors(32)
        rows = []
        cross_scores: dict[str, dict[str, float]] = {}
        for item in bundle.items:
            text_vector = _hash_vector(f"cross:{item.text}")
            relevance = _top_scores({sector: _cosine(text_vector, vector) for sector, vector in sector_vectors.items()})
            cross_scores[item.news_id] = relevance
            rows.append(
                _row_with_scores(
                    spec,
                    context,
                    bundle,
                    item,
                    cache_key,
                    relevance_by_sector=relevance,
                    warnings=("proxy_cross_encoder_reranker_via_shared_encoder",),
                    extra={"cross_encoder_scores": relevance, "reranker_backend": "proxy_shared_hash_encoder"},
                )
            )
        return _result(
            spec,
            AvailabilityStatus.AVAILABLE,
            context,
            bundle,
            cache_key,
            feature_rows=rows,
            availability=report.as_dict(),
            extra_outputs={"daily_features": _daily_summary(rows), "cross_encoder_scores": cross_scores, "interface_only": False},
        )
    if report.status == AvailabilityStatus.AVAILABLE and not is_proxy_report(report):
        try:
            cross_scores = _rerank_with_local_cross_encoder(bundle.items, context, report.local_path)
            rows = []
            for item in bundle.items:
                relevance = _top_scores(cross_scores.get(item.news_id, {}))
                rows.append(
                    _row_with_scores(
                        spec,
                        context,
                        bundle,
                        item,
                        cache_key,
                        relevance_by_sector=relevance,
                        warnings=("local_cross_encoder_reranker",),
                        extra={"cross_encoder_scores": relevance, "reranker_backend": "local_cross_encoder_sequence_classifier"},
                    )
                )
            return _result(
                spec,
                AvailabilityStatus.AVAILABLE,
                context,
                bundle,
                cache_key,
                feature_rows=rows,
                availability=report.as_dict(),
                extra_outputs={
                    "daily_features": _daily_summary(rows),
                    "cross_encoder_scores": cross_scores,
                    "interface_only": False,
                    "reranker_backend": "local_cross_encoder_sequence_classifier",
                },
            )
        except LocalTransformerLoadError as exc:
            report = _load_failure_report(report, exc)
    rows = _fallback_rows(spec, context, bundle, cache_key, fallback_code)
    rows = [{**row, "warnings": tuple(sorted(set(row["warnings"]) | {"interface_only_unavailable"}))} for row in rows]
    return _result(
        spec,
        report.status,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        fallback_code=fallback_code,
        availability=report.as_dict(),
        extra_outputs={"daily_features": _daily_summary(rows), "interface_only": True},
    )


def _run_n7(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    report = check_model_availability(spec, context)
    history = _history_items(payload)
    sector_vectors = _hash_sector_vectors(32) if is_proxy_report(report) and report.status == AvailabilityStatus.AVAILABLE else {}
    rows = []
    for item in bundle.items:
        if sector_vectors:
            text_vector = _hash_vector(f"temporal:{item.text}:{'|'.join(history[-5:])}")
            relevance = _top_scores({sector: _cosine(text_vector, vector) for sector, vector in sector_vectors.items()})
            base_warning = "proxy_temporal_lagged_attention"
        else:
            relevance = _lexical_relevance(item.text)
            base_warning = "temporal_attention_fallback_used"
        warnings = [base_warning]
        if len(history) < 2:
            warnings.append("short_history")
        rows.append(
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                relevance_by_sector=relevance,
                warnings=tuple(warnings),
                extra={
                    "temporal_attention": _temporal_attention(item.text, history),
                    "temporal_backend": "proxy_hash_temporal_attention" if sector_vectors else "fallback_temporal_overlap",
                },
            )
        )
    return _result(
        spec,
        report.status,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        fallback_code="N1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={"daily_features": _daily_summary(rows), "history_count": len(history)},
    )


def _run_n8(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    payload: dict[str, Any] | None = None,
) -> MethodRunResult:
    del payload
    report = check_model_availability(spec, context)
    rows = []
    for item in bundle.items:
        entities = _extract_entities(item.text)
        propagated = _graph_propagation(entities)
        if report.status == AvailabilityStatus.AVAILABLE and is_proxy_report(report):
            warning = ("proxy_static_graph_attention",)
            backend = "proxy_entity_sector_graph_attention"
        else:
            warning = ("graph_attention_fallback_static_edges",)
            backend = "fallback_static_entity_sector_edges"
        rows.append(
            _row_with_scores(
                spec,
                context,
                bundle,
                item,
                cache_key,
                relevance_by_sector=propagated,
                entities=entities,
                warnings=warning,
                extra={"graph_propagation": propagated, "graph_backend": backend},
            )
        )
    return _result(
        spec,
        report.status,
        context,
        bundle,
        cache_key,
        feature_rows=rows,
        fallback_code="N1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={"daily_features": _daily_summary(rows)},
    )


def _run_composite(
    spec: MethodSpec,
    context: MethodRunContext,
    payload: dict[str, Any] | None,
    bundle: VisibleNewsBundle,
    cache_key: str,
) -> MethodRunResult:
    from nlpcc.news_overlay.registry import get_method_spec

    component_results = [RealNewsAnalysisMethod(get_method_spec(code)).run(context, payload) for code in spec.components]
    merged = _merge_component_rows(spec, context, bundle, cache_key, component_results)
    status = AvailabilityStatus.AVAILABLE
    if any(result.status != AvailabilityStatus.AVAILABLE for result in component_results):
        status = AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL
    availability = _composite_availability(spec, context, status, component_results)
    return _result(
        spec,
        status,
        context,
        bundle,
        cache_key,
        feature_rows=merged,
        fallback_code=spec.fallback_code if status != AvailabilityStatus.AVAILABLE else None,
        availability=availability,
        extra_outputs={"daily_features": _daily_summary(merged), "component_traces": [result.as_dict() for result in component_results]},
    )


def _base_feature_row(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    item: NormalizedNewsItem,
    cache_key: str,
    duplicate_cluster_id: str | None = None,
) -> dict[str, Any]:
    timestamp_safe = _timestamp_safe(item, bundle)
    return {
        "method_code": spec.code,
        "news_id": item.news_id,
        "source": item.source,
        "title": item.title,
        "publish_time": item.publish_time.isoformat() if item.publish_time else None,
        "decision_date": bundle.decision_date,
        "cutoff": bundle.cutoff,
        "timestamp_safe": timestamp_safe,
        "event_type": "none",
        "event_probabilities": {},
        "relevance_by_sector": {},
        "aspect_tone": {aspect: 0.0 for aspect in ASPECTS},
        "label_attention_scores": {},
        "sector_query_attention_weights": {},
        "cache_key": cache_key,
        "model_status": "available",
        "device": context.device,
        "fallback_flag": False,
        "duplicate_cluster_id": duplicate_cluster_id or _cluster_id(item.text),
        "entities": (),
        "warnings": () if timestamp_safe else ("timestamp_not_verified",),
    }


def _row_with_scores(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    item: NormalizedNewsItem,
    cache_key: str,
    *,
    duplicate_cluster_id: str | None = None,
    relevance_by_sector: dict[str, float] | None = None,
    aspect_tone: dict[str, float] | None = None,
    event_probabilities: dict[str, float] | None = None,
    label_attention_scores: dict[str, float] | None = None,
    entities: tuple[str, ...] = (),
    fallback_flag: bool = False,
    warnings: tuple[str, ...] = (),
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = _base_feature_row(spec, context, bundle, item, cache_key, duplicate_cluster_id)
    event_probs = event_probabilities or _label_scores(item.text, EVENT_LABELS)
    row.update(
        {
            "event_type": max(event_probs, key=event_probs.get) if event_probs else "none",
            "event_probabilities": event_probs,
            "relevance_by_sector": relevance_by_sector or {},
            "aspect_tone": aspect_tone or _aspect_tone(item.text),
            "label_attention_scores": label_attention_scores or event_probs,
            "entities": entities or _extract_entities(item.text),
            "fallback_flag": fallback_flag,
            "warnings": tuple(sorted(set(row["warnings"]) | set(warnings))),
        }
    )
    if extra:
        row.update(extra)
    return row


def _result(
    spec: MethodSpec,
    status: AvailabilityStatus,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    *,
    feature_rows: list[dict[str, Any]],
    fallback_code: str | None = None,
    availability: dict[str, Any] | None = None,
    extra_outputs: dict[str, Any] | None = None,
) -> MethodRunResult:
    availability_data = availability or {"method_code": spec.code, "status": status.value, "network_attempted": False}
    asset_status = str(availability_data.get("asset_status") or availability_data.get("status") or status.value)
    proxy_flag = bool(availability_data.get("proxy") or asset_status in {"available_proxy_only", "available_via_shared_encoder"})
    rows = [
        {
            **row,
            "model_status": status.value,
            "asset_status": asset_status,
            "proxy_flag": proxy_flag,
            "fallback_flag": bool(row.get("fallback_flag") or fallback_code),
        }
        for row in feature_rows
    ]
    diagnostics = {
        "cache_key": cache_key,
        "cache_hit": False,
        "visible_news_count": len(bundle.items),
        "filter_diagnostics": bundle.diagnostics,
        "availability": availability_data,
    }
    outputs = {
        "feature_rows": rows,
        "required_schema_fields": (
            "timestamp_safe",
            "event_probabilities",
            "relevance_by_sector",
            "aspect_tone",
            "label_attention_scores",
            "sector_query_attention_weights",
            "cache_key",
            "model_status",
            "asset_status",
            "device",
            "fallback_flag",
            "proxy_flag",
            "method_code",
            "warnings",
        ),
        "cache_key": cache_key,
        "model_status": status.value,
        "asset_status": asset_status,
        "proxy_flag": proxy_flag,
    }
    if extra_outputs:
        outputs.update(extra_outputs)
    return MethodRunResult(
        method_code=spec.code,
        kind="N",
        status=status,
        fallback_code=fallback_code,
        transformer_used=spec.transformer_used,
        network_attempted=False,
        outputs=outputs,
        diagnostics=diagnostics,
    )


def _fallback_rows(spec: MethodSpec, context: MethodRunContext, bundle: VisibleNewsBundle, cache_key: str, fallback_code: str) -> list[dict[str, Any]]:
    return [
        _row_with_scores(
            spec,
            context,
            bundle,
            item,
            cache_key,
            relevance_by_sector=_lexical_relevance(item.text),
            aspect_tone=_aspect_tone(item.text),
            event_probabilities=_label_scores(item.text, EVENT_LABELS),
            label_attention_scores=_label_scores(item.text, EVENT_LABELS),
            entities=_extract_entities(item.text),
            fallback_flag=True,
            warnings=(f"fallback_to_{fallback_code}",),
        )
        for item in bundle.items
    ]


def _composite_availability(
    spec: MethodSpec,
    context: MethodRunContext,
    status: AvailabilityStatus,
    component_results: list[MethodRunResult],
) -> dict[str, Any]:
    asset_status = composite_asset_status(component_results)
    metadata = context.local_model_metadata.get(spec.code) or context.local_model_metadata.get(spec.model_identifier or "") or {}
    return {
        "method_code": spec.code,
        "status": status.value,
        "asset_status": asset_status,
        "model_identifier": spec.model_identifier,
        "hf_model_id": metadata.get("hf_model_id"),
        "local_path": model_ref_for_cache(spec, context),
        "revision": metadata.get("revision_or_commit") or metadata.get("revision"),
        "fallback_code": spec.fallback_code,
        "network_attempted": False,
        "local_files_only": True,
        "reason": "composite_component_status",
        "device": context.device,
        "proxy": asset_status in {"available_proxy_only", "available_via_shared_encoder"},
        "transformer_execution": bool(spec.transformer_used and asset_status == "available"),
        "component_asset_status": {
            result.method_code: (result.diagnostics.get("availability") or {}).get("asset_status")
            or (result.diagnostics.get("availability") or {}).get("status")
            for result in component_results
        },
    }


def _load_failure_report(report: ModelAvailabilityReport, exc: LocalTransformerLoadError) -> ModelAvailabilityReport:
    reason = str(exc)
    status = AvailabilityStatus.BLOCKED_MISSING_DEPENDENCY if reason.startswith("missing_dependency:") else AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL
    return ModelAvailabilityReport(
        method_code=report.method_code,
        status=status,
        model_identifier=report.model_identifier,
        hf_model_id=report.hf_model_id,
        local_path=report.local_path,
        revision=report.revision,
        dependency=report.dependency,
        fallback_code=report.fallback_code,
        network_attempted=False,
        local_files_only=True,
        reason=reason,
        device=report.device,
        asset_status=status.value,
    )


def _tokenize(text: str) -> tuple[str, ...]:
    normalized = text.lower()
    tokens = TOKEN_RE.findall(normalized)
    words = list(tokens)
    for keyword_group in list(SECTOR_PROTOTYPES.values()) + list(ASPECT_KEYWORDS.values()) + [POSITIVE_CUES, NEGATIVE_CUES]:
        for keyword in keyword_group:
            if keyword.lower() in normalized:
                words.append(keyword.lower())
    return tuple(words)


def _lexical_relevance(text: str) -> dict[str, float]:
    doc_tokens = _tokenize(text)
    doc_counts = Counter(doc_tokens)
    scores: dict[str, float] = {}
    for sector, keywords in SECTOR_PROTOTYPES.items():
        query_tokens = tuple(token for keyword in keywords for token in _tokenize(keyword))
        overlap = sum(doc_counts[token] for token in query_tokens)
        score = overlap / max(1.0, math.sqrt(len(doc_tokens)) * math.sqrt(len(query_tokens)))
        if score > 0:
            scores[sector] = min(1.0, score)
    return _top_scores(scores)


def _label_scores(text: str, labels: dict[str, str]) -> dict[str, float]:
    doc = set(_tokenize(text))
    raw: dict[str, float] = {}
    for label, description in labels.items():
        label_tokens = set(_tokenize(description))
        raw[label] = len(doc & label_tokens) / max(1, len(label_tokens))
    if not any(raw.values()):
        return {label: round(1.0 / len(raw), 6) for label in raw}
    total = sum(raw.values())
    return {label: round(value / total, 6) for label, value in sorted(raw.items())}


def _softmax_scores(scores: dict[str, float], temperature: float = 4.0) -> dict[str, float]:
    if not scores:
        return {}
    peak = max(scores.values())
    exp_scores = {key: math.exp((float(value) - peak) * temperature) for key, value in scores.items()}
    total = sum(exp_scores.values()) or 1.0
    return {key: round(value / total, 6) for key, value in sorted(exp_scores.items())}


def _aspect_description(aspect: str) -> str:
    keywords = " ".join(ASPECT_KEYWORDS[aspect])
    return f"{aspect}: {keywords}"


def _sector_query_description(sector: str) -> str:
    return f"{sector}: {' '.join(SECTOR_PROTOTYPES[sector])}"


def _scale_aspect_tone(lexical_tone: dict[str, float], aspect_strength: dict[str, float]) -> dict[str, float]:
    return {
        aspect: round(float(lexical_tone.get(aspect, 0.0)) * (0.5 + 0.5 * float(aspect_strength.get(aspect, 0.0))), 6)
        for aspect in ASPECTS
    }


def _aspect_tone(text: str) -> dict[str, float]:
    text_lower = text.lower()
    positive = sum(1 for cue in POSITIVE_CUES if cue.lower() in text_lower)
    negative = sum(1 for cue in NEGATIVE_CUES if cue.lower() in text_lower)
    base = (positive - negative) / max(1, positive + negative)
    return {
        aspect: round(base if any(keyword.lower() in text_lower for keyword in keywords) else base * 0.35, 6)
        for aspect, keywords in ASPECT_KEYWORDS.items()
    }


def _extract_entities(text: str) -> tuple[str, ...]:
    text_lower = text.lower()
    entities = [sector for sector, keywords in SECTOR_PROTOTYPES.items() if any(keyword.lower() in text_lower for keyword in keywords)]
    return tuple(dict.fromkeys(entities))


def _event_arguments(text: str, label_scores: dict[str, float]) -> dict[str, Any]:
    top_label = max(label_scores, key=label_scores.get) if label_scores else "none"
    text_tokens = _tokenize(text)
    return {
        "event_type": top_label,
        "entities": _extract_entities(text),
        "trigger_terms": tuple(token for token in _tokenize(EVENT_LABELS.get(top_label, "")) if token in text_tokens)[:8],
    }


def _duplicate_clusters(items: tuple[NormalizedNewsItem, ...]) -> dict[str, str]:
    clusters: dict[str, str] = {}
    seen: dict[str, str] = {}
    for item in items:
        key = _cluster_id(item.title or item.text)
        cluster = seen.setdefault(key, f"dup_{len(seen) + 1:03d}")
        clusters[item.news_id] = cluster
    return clusters


def _cluster_id(text: str) -> str:
    compact = re.sub(r"\s+", "", text.lower())[:48]
    return sha256(compact.encode("utf-8")).hexdigest()[:12]


def _timestamp_safe(item: NormalizedNewsItem, bundle: VisibleNewsBundle) -> bool:
    if item.publish_time is None or bundle.decision_date == "unknown":
        return True
    try:
        decision = datetime.strptime(bundle.decision_date.replace("-", "")[:8], "%Y%m%d").date()
    except ValueError:
        return True
    if item.publish_time.date() > decision:
        return False
    if item.publish_time.date() == decision:
        cutoff_hour, cutoff_minute = (int(part) for part in bundle.cutoff.split(":")[:2])
        return (item.publish_time.hour, item.publish_time.minute) < (cutoff_hour, cutoff_minute)
    return True


def _daily_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    relevance: dict[str, float] = {}
    attention: dict[str, float] = {}
    for row in rows:
        for sector, value in row.get("relevance_by_sector", {}).items():
            relevance[sector] = relevance.get(sector, 0.0) + float(value)
        for sector, value in row.get("sector_query_attention_weights", {}).items():
            attention[sector] = attention.get(sector, 0.0) + float(value)
    return {
        "relevance_by_sector": _top_scores(relevance),
        "attention_mass_by_sector": _top_scores(attention),
        "news_count": len(rows),
        "warnings": tuple(sorted({warning for row in rows for warning in row.get("warnings", ())})),
    }


def _sector_attention(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    sectors = sorted({sector for row in rows for sector in row.get("relevance_by_sector", {})})
    attention: dict[str, dict[str, float]] = {}
    for sector in sectors:
        values = [(row["news_id"], float(row.get("relevance_by_sector", {}).get(sector, 0.0))) for row in rows]
        exp_values = [(news_id, math.exp(value)) for news_id, value in values]
        total = sum(value for _, value in exp_values) or 1.0
        attention[sector] = {news_id: round(value / total, 6) for news_id, value in exp_values}
    return attention


def _history_items(payload: dict[str, Any] | None) -> tuple[str, ...]:
    history = (payload or {}).get("history") or (payload or {}).get("lagged_news") or ()
    texts = []
    for row in history:
        if isinstance(row, dict):
            texts.append(" ".join(str(row.get(key, "") or "") for key in ("title", "TITLE", "content", "CONTENT")).strip())
        else:
            texts.append(str(row))
    return tuple(text for text in texts if text)


def _temporal_attention(text: str, history: tuple[str, ...]) -> dict[str, float]:
    if not history:
        return {}
    doc = set(_tokenize(text))
    scores = []
    for index, item in enumerate(history[-5:]):
        lag_tokens = set(_tokenize(item))
        overlap = len(doc & lag_tokens) / max(1, len(doc | lag_tokens))
        recency = 1.0 / (len(history[-5:]) - index)
        scores.append((f"lag_{len(history[-5:]) - index}", overlap * recency))
    total = sum(value for _, value in scores) or 1.0
    return {key: round(value / total, 6) for key, value in scores}


def _graph_propagation(entities: tuple[str, ...]) -> dict[str, float]:
    propagation = {entity: 1.0 for entity in entities if entity in SECTOR_PROTOTYPES}
    if "bank" in propagation:
        propagation["brokerage"] = max(propagation.get("brokerage", 0.0), 0.45)
        propagation["broad_market"] = max(propagation.get("broad_market", 0.0), 0.35)
    if "semiconductor" in propagation:
        propagation["ai"] = max(propagation.get("ai", 0.0), 0.4)
        propagation["software"] = max(propagation.get("software", 0.0), 0.25)
    return _top_scores(propagation)


def _merge_component_rows(
    spec: MethodSpec,
    context: MethodRunContext,
    bundle: VisibleNewsBundle,
    cache_key: str,
    component_results: list[MethodRunResult],
) -> list[dict[str, Any]]:
    by_news: dict[str, dict[str, Any]] = {}
    for result in component_results:
        for row in result.outputs.get("feature_rows", ()):
            target = by_news.setdefault(row["news_id"], _base_feature_row(spec, context, bundle, _find_item(bundle, row["news_id"]), cache_key))
            for key in ("event_probabilities", "relevance_by_sector", "aspect_tone", "label_attention_scores", "sector_query_attention_weights"):
                target[key] = _merge_score_dicts(target.get(key, {}), row.get(key, {}))
            target["entities"] = tuple(dict.fromkeys(tuple(target.get("entities", ())) + tuple(row.get("entities", ()))))
            target["warnings"] = tuple(sorted(set(target.get("warnings", ())) | set(row.get("warnings", ()))))
            target["fallback_flag"] = bool(target.get("fallback_flag") or row.get("fallback_flag"))
            target.setdefault("component_methods", []).append(result.method_code)
    return list(by_news.values())


def _find_item(bundle: VisibleNewsBundle, news_id: str) -> NormalizedNewsItem:
    for item in bundle.items:
        if item.news_id == news_id:
            return item
    raise KeyError(news_id)


def _merge_score_dicts(first: dict[str, float], second: dict[str, float]) -> dict[str, float]:
    merged = dict(first)
    for key, value in second.items():
        merged[key] = round(max(float(merged.get(key, 0.0)), float(value)), 6)
    return merged


def _top_scores(scores: dict[str, float], limit: int = 8) -> dict[str, float]:
    return {
        key: round(float(value), 6)
        for key, value in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
        if value > 0
    }


def _hash_vector(text: str, dims: int = 32) -> list[float]:
    values = []
    for index in range(dims):
        digest = sha256(f"{index}:{text}".encode("utf-8")).digest()
        values.append((int.from_bytes(digest[:4], "little") / 2**32) * 2 - 1)
    norm = math.sqrt(sum(value * value for value in values)) or 1.0
    return [value / norm for value in values]


def _hash_sector_vectors(dims: int) -> dict[str, list[float]]:
    return {sector: _hash_vector(" ".join(keywords), dims) for sector, keywords in SECTOR_PROTOTYPES.items()}


def _cosine(first: list[float], second: list[float]) -> float:
    denom = (math.sqrt(sum(value * value for value in first)) or 1.0) * (math.sqrt(sum(value * value for value in second)) or 1.0)
    return round(max(0.0, sum(a * b for a, b in zip(first, second)) / denom), 6)


def _should_use_sequence_classifier(context: MethodRunContext, spec: MethodSpec, report: ModelAvailabilityReport) -> bool:
    metadata = context.local_model_metadata.get(spec.code) or context.local_model_metadata.get(spec.model_identifier or "") or {}
    role = str(metadata.get("role") or "").lower()
    hf_model_id = str(report.hf_model_id or metadata.get("hf_model_id") or "").lower()
    return any(token in role for token in ("sentiment", "finbert")) or any(
        token in hf_model_id for token in ("sentiment", "finbert")
    )


def _classify_with_local_sequence_classifier(
    texts: tuple[str, ...],
    context: MethodRunContext,
    local_path: str | None,
) -> list[dict[str, Any]]:
    if not texts:
        return []
    probabilities, labels = _sequence_classifier_probabilities(texts, None, context, local_path)
    rows = []
    for probs in probabilities:
        labelled = {labels[index]: round(float(value), 6) for index, value in enumerate(probs)}
        score = _sentiment_score(labelled)
        rows.append(
            {
                "probabilities": labelled,
                "label": max(labelled, key=labelled.get) if labelled else "unknown",
                "sentiment_score": round(score, 6),
            }
        )
    return rows


def _rerank_with_local_cross_encoder(
    items: tuple[NormalizedNewsItem, ...],
    context: MethodRunContext,
    local_path: str | None,
) -> dict[str, dict[str, float]]:
    if not items:
        return {}
    sector_names = tuple(SECTOR_PROTOTYPES)
    left_texts = []
    right_texts = []
    for item in items:
        for sector in sector_names:
            left_texts.append(item.text)
            right_texts.append(_sector_query_description(sector))
    probabilities, _labels = _sequence_classifier_probabilities(tuple(left_texts), tuple(right_texts), context, local_path)
    raw_scores = [_reranker_score(probs) for probs in probabilities]
    result: dict[str, dict[str, float]] = {}
    cursor = 0
    for item in items:
        sector_scores = {
            sector: raw_scores[cursor + index]
            for index, sector in enumerate(sector_names)
        }
        cursor += len(sector_names)
        result[item.news_id] = _softmax_scores(sector_scores, temperature=1.0)
    return result


def _sequence_classifier_probabilities(
    texts: tuple[str, ...],
    pair_texts: tuple[str, ...] | None,
    context: MethodRunContext,
    local_path: str | None,
) -> tuple[list[list[float]], list[str]]:
    if not local_path:
        raise LocalTransformerLoadError("local_path_missing_during_load")
    try:
        import torch  # type: ignore
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
    except Exception as exc:
        raise LocalTransformerLoadError(f"missing_dependency:torch_or_transformers:{exc.__class__.__name__}") from exc
    try:
        device = _runtime_device(context, torch)
        tokenizer, model = _cached_local_model(
            "sequence_classifier",
            local_path,
            device,
            AutoTokenizer,
            AutoModelForSequenceClassification,
        )
        batch_size = max(1, int(context.batch_size or 16))
        all_probs: list[list[float]] = []
        labels: list[str] = []
        max_length = 256
        autocast_enabled = device == "cuda"
        for start in range(0, len(texts), batch_size):
            stop = start + batch_size
            text_batch = list(texts[start:stop])
            if pair_texts is None:
                encoded = tokenizer(text_batch, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            else:
                encoded = tokenizer(text_batch, list(pair_texts[start:stop]), padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad(), torch.autocast("cuda", enabled=autocast_enabled, dtype=torch.float16):
                logits = model(**encoded).logits
                if logits.shape[-1] == 1:
                    probs = torch.sigmoid(logits)
                    labels = ["relevance"]
                else:
                    probs = torch.nn.functional.softmax(logits, dim=-1)
                    labels = _classifier_labels(model, logits.shape[-1])
            all_probs.extend([[float(value) for value in row] for row in probs.cpu().tolist()])
        return all_probs, labels
    except Exception as exc:
        raise LocalTransformerLoadError(f"local_sequence_classifier_load_failed:{exc.__class__.__name__}") from exc


def _classifier_labels(model: Any, width: int) -> list[str]:
    id2label = getattr(getattr(model, "config", None), "id2label", {}) or {}
    labels = []
    for index in range(width):
        labels.append(str(id2label.get(index, id2label.get(str(index), f"LABEL_{index}"))))
    return labels


def _sentiment_score(probabilities: dict[str, float]) -> float:
    positive = 0.0
    negative = 0.0
    for label, value in probabilities.items():
        normalized = str(label).lower()
        if "pos" in normalized or normalized in {"label_1", "1"}:
            positive += float(value)
        elif "neg" in normalized or normalized in {"label_0", "0"}:
            negative += float(value)
    if positive == 0.0 and negative == 0.0 and len(probabilities) >= 2:
        values = list(probabilities.values())
        negative = float(values[0])
        positive = float(values[-1])
    return max(-1.0, min(1.0, positive - negative))


def _aspect_tone_from_sentiment(text: str, sentiment_score: float) -> dict[str, float]:
    lexical = _aspect_tone(text)
    text_lower = text.lower()
    values = {}
    for aspect, keywords in ASPECT_KEYWORDS.items():
        active = any(keyword.lower() in text_lower for keyword in keywords)
        scale = 1.0 if active else 0.35
        lexical_hint = abs(float(lexical.get(aspect, 0.0)))
        values[aspect] = round(float(sentiment_score) * max(scale, lexical_hint), 6)
    return values


def _reranker_score(probabilities: list[float]) -> float:
    if not probabilities:
        return 0.0
    if len(probabilities) == 1:
        return float(probabilities[0])
    return float(probabilities[-1])


def _encode_with_local_transformer(texts: tuple[str, ...], context: MethodRunContext, local_path: str | None) -> list[list[float]]:
    if not texts:
        return []
    if not local_path:
        raise LocalTransformerLoadError("local_path_missing_during_load")
    try:
        import torch  # type: ignore
        from transformers import AutoModel, AutoTokenizer  # type: ignore
    except Exception as exc:
        raise LocalTransformerLoadError(f"missing_dependency:torch_or_transformers:{exc.__class__.__name__}") from exc
    try:
        device = _runtime_device(context, torch)
        tokenizer, model = _cached_local_model("encoder", local_path, device, AutoTokenizer, AutoModel)
        batch_size = max(1, int(context.batch_size or 16))
        autocast_enabled = device == "cuda"
        rows: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            text_batch = list(texts[start : start + batch_size])
            encoded = tokenizer(text_batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad(), torch.autocast("cuda", enabled=autocast_enabled, dtype=torch.float16):
                output = model(**encoded)
                hidden = output.last_hidden_state
                mask = encoded["attention_mask"].unsqueeze(-1)
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            rows.extend([[float(value) for value in row] for row in pooled.cpu().tolist()])
        return rows
    except Exception as exc:
        raise LocalTransformerLoadError(f"local_transformer_load_failed:{exc.__class__.__name__}") from exc


def _runtime_device(context: MethodRunContext, torch_module: Any) -> str:
    return context.device if context.device == "cuda" and getattr(torch_module.cuda, "is_available", lambda: False)() else "cpu"


def _cached_local_model(
    role: str,
    local_path: str,
    device: str,
    tokenizer_cls: Any,
    model_cls: Any,
) -> tuple[Any, Any]:
    key = (role, str(Path(local_path).resolve()), device)
    cached = _LOCAL_MODEL_CACHE.get(key)
    if cached is not None:
        return cached
    tokenizer = tokenizer_cls.from_pretrained(local_path, local_files_only=True)
    model = model_cls.from_pretrained(local_path, local_files_only=True)
    model.to(device)
    model.eval()
    _LOCAL_MODEL_CACHE[key] = (tokenizer, model)
    return tokenizer, model
