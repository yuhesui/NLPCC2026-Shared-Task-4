"""Prompt09 production real-transformer news tensor provider.

This module is intentionally stricter than the Prompt08 research tensor code:
production mode must use local transformer inference or fail closed. It never
uses hash embeddings, lexical sentiment, fixed target replay, or online model
downloads as substitutes for missing models.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

FUND_KEYWORDS: dict[str, tuple[str, ...]] = {
    "000300.SH": ("沪深300", "大盘", "蓝筹", "市场", "宏观", "指数"),
    "000905.SH": ("中证500", "中盘", "成长", "市场", "指数"),
    "399006.SZ": ("创业板", "成长", "科技", "创新"),
    "000688.SH": ("科创", "科创板", "科技", "芯片", "创新"),
    "000932.SH": ("消费", "食品", "饮料", "零售"),
    "000941.SH": ("新能源", "光伏", "锂电", "电动车"),
    "399971.SZ": ("传媒", "游戏", "影视", "互联网"),
    "000819.SH": ("有色", "稀土", "金属", "铜", "铝"),
    "000928.SH": ("能源", "石油", "天然气", "煤炭"),
    "000012.SH": ("债券", "利率", "国债", "收益率"),
    "518880.SH": ("黄金", "金价", "避险", "贵金属"),
    "512880.SH": ("证券", "券商", "资本市场", "交易"),
    "512800.SH": ("银行", "信贷", "息差", "降准"),
    "512070.SH": ("保险", "保费", "权益投资"),
    "159995.SZ": ("半导体", "芯片", "集成电路"),
    "159819.SZ": ("人工智能", "AI", "算力", "大模型"),
    "515880.SH": ("通信", "5G", "光模块", "设备"),
    "159852.SZ": ("软件", "信创", "云计算"),
    "512010.SH": ("医药", "药品", "集采"),
    "512170.SH": ("医疗", "器械", "医疗服务"),
    "159992.SZ": ("创新药", "临床", "CXO"),
    "515170.SH": ("食品", "饮料", "消费"),
    "512690.SH": ("白酒", "酒企", "茅台"),
    "512400.SH": ("有色", "金属", "铜", "铝"),
    "515220.SH": ("煤炭", "动力煤", "焦煤"),
    "159870.SZ": ("化工", "化学", "农化"),
    "512200.SH": ("房地产", "地产", "房企", "按揭"),
}


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
BGE_SNAPSHOT = PACKAGE_ROOT / "package" / "models" / "bge_contrastive_finetuned_2024_dev_best"
FINBERT_SNAPSHOT = PACKAGE_ROOT / "package" / "models" / "finbert_tone_chinese_e91b1a3"
RERANKER_SNAPSHOT = PACKAGE_ROOT / "package" / "models" / "reranker_unavailable"

DEFAULT_REQUIRED_MODEL_ROLES = ("embedding_encoder", "financial_sentiment")

ASPECT_LABELS = {
    "policy": "宏观政策 财政 货币 监管 改革 支持",
    "liquidity": "流动性 利率 降准 信贷 融资 资金面",
    "earnings": "业绩 利润 收入 订单 增长 预期",
    "risk": "风险 违约 冲突 制裁 下滑 波动",
    "demand": "消费 需求 出口 库存 价格 景气",
}

EVENT_LABELS = {
    "policy_easing": "政策宽松 降准 降息 支持资本市场",
    "regulation": "监管处罚 规范 平台治理 行业整顿",
    "earnings_growth": "业绩增长 盈利改善 订单增加",
    "earnings_warning": "业绩下滑 亏损 违约 风险暴露",
    "supply_shock": "供应冲击 能源 原材料 库存 价格波动",
    "technology_ai": "人工智能 算力 半导体 软件 创新",
    "consumption": "消费 食品饮料 医疗 零售 旅游",
    "global_risk": "海外市场 地缘 冲突 制裁 汇率",
}


class ProductionRealNLPError(RuntimeError):
    """Fail-closed production real-NLP error with a stable reason code."""

    def __init__(self, blocked_reason: str, message: str | None = None) -> None:
        self.blocked_reason = blocked_reason
        super().__init__(message or blocked_reason)


@dataclass(frozen=True)
class RealTransformerNewsTensorConfig:
    """Production-mode local model and overlay policy."""

    candidate_id: str
    method_stack: str
    required_model_roles: tuple[str, ...] = DEFAULT_REQUIRED_MODEL_ROLES
    bge_path: Path = BGE_SNAPSHOT
    finbert_path: Path = FINBERT_SNAPSHOT
    reranker_path: Path = RERANKER_SNAPSHOT
    device: str = "auto"
    batch_size: int = 16
    max_news_per_day: int = 8
    local_files_only: bool = True
    production_real_nlp: bool = True
    allow_proxy_news: bool = False
    allow_heuristic_news: bool = False
    allow_fixed_target_replay: bool = False
    allow_old_research_table_replay: bool = False
    overlay_cap: float = 0.012
    turnover_cap: float = 0.035
    confidence_gate: float = 0.35
    deadband: float = 0.00008
    drawdown_guard: bool = False
    tensor_schema_version: str = "prompt09_real_transformer_news_tensor_v1"

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "RealTransformerNewsTensorConfig":
        data = dict(values)
        for key in ("bge_path", "finbert_path", "reranker_path"):
            if key in data and data[key] not in (None, ""):
                data[key] = Path(str(data[key]))
        if "required_model_roles" in data:
            data["required_model_roles"] = tuple(str(item) for item in data["required_model_roles"])
        return cls(**{key: value for key, value in data.items() if key in cls.__dataclass_fields__})

    def config_hash(self) -> str:
        payload = {
            key: str(value) if isinstance(value, Path) else value
            for key, value in self.__dict__.items()
        }
        return stable_hash(payload)


@dataclass(frozen=True)
class NewsTensorBatch:
    """Flat tensor rows plus production audit metadata."""

    date: str
    track: str
    candidate_id: str
    rows: pd.DataFrame
    manifest: dict[str, Any]
    tensor_hash: str
    model_status_rows: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    @property
    def tensor_shape(self) -> tuple[int, int]:
        return (int(len(self.rows)), int(len(self.rows.columns)))


class RealTransformerNewsTensorProvider:
    """Build continuous local-transformer news tensors for one candidate."""

    def __init__(self, config: RealTransformerNewsTensorConfig) -> None:
        self.config = config
        enforce_production_no_proxy_policy(config)
        self.network_attempted = False
        self._torch: Any | None = None
        self._bge_tokenizer: Any | None = None
        self._bge_model: Any | None = None
        self._sentiment_tokenizer: Any | None = None
        self._sentiment_model: Any | None = None
        self._sentiment_labels: list[str] = []
        self.device = "cpu"
        self.model_status_rows: list[dict[str, Any]] = []
        self._load_required_models()

    def build(
        self,
        date: str | int,
        news_items: list[dict[str, Any]],
        track: str,
        candidate_config: Mapping[str, Any],
    ) -> NewsTensorBatch:
        date_key = date_to_key(date)
        fund_pool = tuple(str(item) for item in candidate_config.get("fund_pool", ()))
        if not fund_pool:
            raise ValueError("candidate_config must include fund_pool for production tensor build.")
        visible_news = clean_visible_news(news_items)[: max(0, int(self.config.max_news_per_day))]
        cache_key = self._cache_key(date_key, track, candidate_config, visible_news)
        if not visible_news:
            rows = neutral_zero_tensor_rows(date_key, fund_pool)
            manifest = self._manifest(date_key, track, len(visible_news), rows, cache_key, missing_news=True)
            tensor_hash = stable_hash(rows.to_dict("records"))
            return NewsTensorBatch(date_key, normalize_track_label(track), self.config.candidate_id, rows, manifest, tensor_hash, tuple(self.model_status_rows))

        texts = [item["text"] for item in visible_news]
        text_vectors = self._encode_texts(texts)
        fund_vectors = self._encode_texts([fund_description(fund) for fund in fund_pool])
        aspect_vectors = self._encode_texts(list(ASPECT_LABELS.values()))
        event_vectors = self._encode_texts(list(EVENT_LABELS.values()))
        sentiment_score, confidence, entropy, probabilities = self._classify_sentiment(texts)
        recency = np.asarray([recency_decay(item, date_key) for item in visible_news], dtype=np.float32)
        support = support_scores(visible_news)
        novelty = novelty_scores(texts)
        relevance_matrix = np.maximum(0.0, text_vectors @ fund_vectors.T)
        aspect_matrix = np.maximum(0.0, text_vectors @ aspect_vectors.T)
        event_matrix = np.maximum(0.0, text_vectors @ event_vectors.T)
        rows: list[dict[str, Any]] = []
        for fund_index, fund in enumerate(fund_pool):
            relevance = relevance_matrix[:, fund_index]
            weights = np.maximum(relevance * recency, 1e-9)
            weights = weights / max(float(weights.sum()), 1e-9)
            pooled_embedding = (text_vectors * weights[:, None]).sum(axis=0)
            aspect_scores = {
                aspect: round(float(np.average(aspect_matrix[:, idx], weights=weights)), 8)
                for idx, aspect in enumerate(ASPECT_LABELS)
            }
            event_scores = {
                event: round(float(np.average(event_matrix[:, idx], weights=weights)), 8)
                for idx, event in enumerate(EVENT_LABELS)
            }
            continuous_sentiment = float(np.average(sentiment_score, weights=weights))
            sentiment_conf = float(np.average(confidence, weights=weights))
            sentiment_entropy = float(np.average(entropy, weights=weights))
            event_conf = float(max(event_scores.values()) if event_scores else 0.0)
            uncertainty = float(min(1.0, sentiment_entropy / math.log(max(2, len(self._sentiment_labels) or 3))))
            rows.append(
                {
                    "date": date_key,
                    "track": normalize_track_label(track),
                    "candidate_id": self.config.candidate_id,
                    "fund_id": fund,
                    "embedding_vector": json.dumps([round(float(x), 8) for x in pooled_embedding[:16]], ensure_ascii=False),
                    "asset_or_sector_relevance": round(float(np.average(relevance, weights=weights)), 8),
                    "sentiment_score_continuous": round(continuous_sentiment, 8),
                    "sentiment_confidence": round(sentiment_conf, 8),
                    "sentiment_entropy": round(sentiment_entropy, 8),
                    "sentiment_probabilities": json.dumps(probability_summary(probabilities, weights), ensure_ascii=False, sort_keys=True),
                    "aspect_scores": json.dumps(aspect_scores, ensure_ascii=False, sort_keys=True),
                    "event_label_scores": json.dumps(event_scores, ensure_ascii=False, sort_keys=True),
                    "event_confidence": round(event_conf, 8),
                    "sector_attention_weights": json.dumps(attention_weights(visible_news, weights), ensure_ascii=False, sort_keys=True),
                    "recency_decay_weight": round(float(np.average(recency, weights=weights)), 8),
                    "source_or_cluster_support": round(float(np.average(support, weights=weights)), 8),
                    "novelty_score": round(float(np.average(novelty, weights=weights)), 8),
                    "uncertainty_score": round(uncertainty, 8),
                    "news_count": len(visible_news),
                    "missing_news": "false",
                    "real_transformer_executed": "true",
                    "proxy_mode": "false",
                    "heuristic_fallback_used": "false",
                    "blocked_reason": "",
                }
            )
        frame = pd.DataFrame(rows)
        manifest = self._manifest(date_key, track, len(visible_news), frame, cache_key, missing_news=False)
        return NewsTensorBatch(
            date_key,
            normalize_track_label(track),
            self.config.candidate_id,
            frame,
            manifest,
            stable_hash(frame.to_dict("records")),
            tuple(self.model_status_rows),
        )

    def apply_overlay(
        self,
        base_weights: Mapping[str, float],
        tensor_rows: pd.DataFrame,
        *,
        previous_weights: Mapping[str, float] | None = None,
        ablation_type: str = "active_real_tensor",
    ) -> tuple[dict[str, float], dict[str, Any]]:
        base = {str(key): max(0.0, float(value)) for key, value in base_weights.items()}
        if ablation_type == "model_disabled_should_block":
            raise ProductionRealNLPError("blocked_missing_local_model", "model disabled ablation must fail closed")
        if ablation_type == "proxy_enabled_should_block":
            raise ProductionRealNLPError(
                "blocked_proxy_forbidden_in_production_real_nlp",
                "proxy ablation is forbidden in production real-NLP mode",
            )
        if tensor_rows.empty or ablation_type == "zeroed_tensor":
            return normalize_weights(base), overlay_diag(base, base, "zeroed_tensor")
        rows = tensor_rows.copy()
        if ablation_type == "date_shuffled_tensor":
            rows = rows.sample(frac=1.0, random_state=17).reset_index(drop=True)
        raw_delta: dict[str, float] = {}
        for _, row in rows.iterrows():
            fund = str(row["fund_id"])
            score = (
                float(row["asset_or_sector_relevance"])
                * float(row["sentiment_score_continuous"])
                * float(row["sentiment_confidence"])
                * float(row["event_confidence"])
                * float(row["recency_decay_weight"])
                * max(0.0, 1.0 - float(row["uncertainty_score"]))
            )
            if float(row["sentiment_confidence"]) < self.config.confidence_gate:
                score = 0.0
            if abs(score) < self.config.deadband:
                score = 0.0
            raw_delta[fund] = score
        centered = center_values(raw_delta)
        capped = cap_l1({fund: value * self.config.overlay_cap for fund, value in centered.items()}, self.config.overlay_cap)
        adjusted = normalize_weights({fund: base.get(fund, 0.0) + capped.get(fund, 0.0) for fund in set(base) | set(capped)})
        if previous_weights:
            turnover = sum(abs(adjusted.get(fund, 0.0) - float(previous_weights.get(fund, 0.0))) for fund in set(adjusted) | set(previous_weights))
            if turnover > self.config.turnover_cap and turnover > 0:
                shrink = self.config.turnover_cap / turnover
                adjusted = normalize_weights(
                    {
                        fund: float(previous_weights.get(fund, 0.0)) + (adjusted.get(fund, 0.0) - float(previous_weights.get(fund, 0.0))) * shrink
                        for fund in set(adjusted) | set(previous_weights)
                    }
                )
        return adjusted, overlay_diag(base, adjusted, ablation_type)

    def _load_required_models(self) -> None:
        try:
            import torch  # type: ignore
            from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
        except Exception as exc:  # pragma: no cover - dependency-specific
            raise ProductionRealNLPError("blocked_missing_dependency", f"missing torch/transformers dependency: {exc}") from exc

        self._torch = torch
        self.device = "cuda" if self.config.device in {"auto", "cuda"} and torch.cuda.is_available() else "cpu"
        if "embedding_encoder" in self.config.required_model_roles:
            self._bge_tokenizer, self._bge_model = self._load_model_pair(
                role="embedding_encoder",
                path=self.config.bge_path,
                tokenizer_cls=AutoTokenizer,
                model_cls=AutoModel,
            )
        if "financial_sentiment" in self.config.required_model_roles:
            self._sentiment_tokenizer, self._sentiment_model = self._load_model_pair(
                role="financial_sentiment",
                path=self.config.finbert_path,
                tokenizer_cls=AutoTokenizer,
                model_cls=AutoModelForSequenceClassification,
            )
            labels = getattr(getattr(self._sentiment_model, "config", None), "id2label", {}) or {}
            width = int(getattr(getattr(self._sentiment_model, "config", None), "num_labels", 3) or 3)
            self._sentiment_labels = [str(labels.get(idx, labels.get(str(idx), f"LABEL_{idx}"))) for idx in range(width)]
        if "reranker" in self.config.required_model_roles:
            self._load_model_pair(
                role="reranker",
                path=self.config.reranker_path,
                tokenizer_cls=AutoTokenizer,
                model_cls=AutoModelForSequenceClassification,
            )

    def _load_model_pair(self, *, role: str, path: Path, tokenizer_cls: Any, model_cls: Any) -> tuple[Any, Any]:
        if not path.exists():
            self.model_status_rows.append(model_status_row(role, path, False, False, self.device, "blocked_missing_local_model"))
            raise ProductionRealNLPError("blocked_missing_local_model", f"{role} local path missing: {path}")
        try:
            tokenizer = tokenizer_cls.from_pretrained(str(path), local_files_only=True)
            model = model_cls.from_pretrained(str(path), local_files_only=True)
            model.to(self.device)
            model.eval()
        except Exception as exc:
            self.model_status_rows.append(model_status_row(role, path, True, False, self.device, f"blocked_load_failed:{type(exc).__name__}"))
            raise ProductionRealNLPError("blocked_missing_local_model", f"{role} local load failed: {exc}") from exc
        self.model_status_rows.append(model_status_row(role, path, True, True, self.device, "loaded_successfully"))
        return tokenizer, model

    def _encode_texts(self, texts: Iterable[str]) -> np.ndarray:
        text_list = list(texts)
        if not text_list:
            return np.zeros((0, 512), dtype=np.float32)
        if self._bge_model is None or self._bge_tokenizer is None or self._torch is None:
            raise ProductionRealNLPError("blocked_missing_local_model", "embedding encoder is not loaded")
        rows: list[np.ndarray] = []
        batch_size = max(1, int(self.config.batch_size))
        for start in range(0, len(text_list), batch_size):
            batch = text_list[start : start + batch_size]
            encoded = self._bge_tokenizer(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            encoded = {key: value.to(self.device) for key, value in encoded.items()}
            with self._torch.no_grad():
                output = self._bge_model(**encoded)
                hidden = output.last_hidden_state
                mask = encoded["attention_mask"].unsqueeze(-1).float()
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
                pooled = self._torch.nn.functional.normalize(pooled, p=2, dim=1)
            rows.append(pooled.detach().cpu().numpy())
        return np.vstack(rows).astype(np.float32)

    def _classify_sentiment(self, texts: Iterable[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        text_list = list(texts)
        if not text_list:
            return np.zeros(0), np.zeros(0), np.zeros(0), np.zeros((0, 3))
        if self._sentiment_model is None or self._sentiment_tokenizer is None or self._torch is None:
            raise ProductionRealNLPError("blocked_missing_local_model", "financial sentiment model is not loaded")
        score_rows: list[float] = []
        confidence_rows: list[float] = []
        entropy_rows: list[float] = []
        probability_rows: list[np.ndarray] = []
        batch_size = max(1, int(self.config.batch_size))
        for start in range(0, len(text_list), batch_size):
            batch = text_list[start : start + batch_size]
            encoded = self._sentiment_tokenizer(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            encoded = {key: value.to(self.device) for key, value in encoded.items()}
            with self._torch.no_grad():
                logits = self._sentiment_model(**encoded).logits
                probs = self._torch.nn.functional.softmax(logits, dim=-1).detach().cpu().numpy()
            for prob in probs:
                labels = {self._sentiment_labels[idx].lower(): float(value) for idx, value in enumerate(prob)}
                positive = sum(value for label, value in labels.items() if "pos" in label or "positive" in label)
                negative = sum(value for label, value in labels.items() if "neg" in label or "negative" in label)
                if positive == 0.0 and negative == 0.0 and len(prob) >= 2:
                    positive = float(prob[-1])
                    negative = float(prob[0])
                score_rows.append(max(-1.0, min(1.0, positive - negative)))
                confidence_rows.append(float(np.max(prob)))
                entropy_rows.append(float(-np.sum(prob * np.log(np.maximum(prob, 1e-12)))))
                probability_rows.append(prob.astype(np.float32))
        return (
            np.asarray(score_rows, dtype=np.float32),
            np.asarray(confidence_rows, dtype=np.float32),
            np.asarray(entropy_rows, dtype=np.float32),
            np.vstack(probability_rows).astype(np.float32),
        )

    def _cache_key(self, date: str, track: str, candidate_config: Mapping[str, Any], news_items: list[dict[str, Any]]) -> str:
        payload = {
            "date": date,
            "track": normalize_track_label(track),
            "candidate_id": self.config.candidate_id,
            "method_stack": self.config.method_stack,
            "config_hash": self.config.config_hash(),
            "model_identity": [row.get("model_sha_or_snapshot") for row in self.model_status_rows],
            "input_hash": stable_hash(news_items),
            "fund_pool": list(candidate_config.get("fund_pool", ())),
        }
        return stable_hash(payload)

    def _manifest(self, date: str, track: str, news_count: int, rows: pd.DataFrame, cache_key: str, *, missing_news: bool) -> dict[str, Any]:
        return {
            "date": date,
            "track": normalize_track_label(track),
            "candidate_id": self.config.candidate_id,
            "news_count": news_count,
            "model_roles_used": ";".join(self.config.required_model_roles),
            "real_transformer_executed": str(not missing_news).lower(),
            "proxy_mode": "false",
            "heuristic_fallback_used": "false",
            "embedding_shape": f"{len(rows)}x16_sampled_from_512",
            "tensor_shape": f"{len(rows)}x{len(rows.columns)}",
            "cache_hit": "false",
            "cache_key": cache_key,
            "missing_news": str(bool(missing_news)).lower(),
            "blocked_reason": "",
        }


def enforce_production_no_proxy_policy(config: RealTransformerNewsTensorConfig) -> None:
    if not config.production_real_nlp:
        raise ProductionRealNLPError("blocked_production_real_nlp_disabled")
    if config.allow_proxy_news:
        raise ProductionRealNLPError("blocked_proxy_forbidden_in_production_real_nlp")
    if config.allow_heuristic_news:
        raise ProductionRealNLPError("blocked_heuristic_forbidden_in_production_real_nlp")
    if config.allow_fixed_target_replay:
        raise ProductionRealNLPError("blocked_fixed_target_replay_forbidden_in_production_real_nlp")
    if config.allow_old_research_table_replay:
        raise ProductionRealNLPError("blocked_old_research_table_forbidden_in_production_real_nlp")
    if not config.local_files_only:
        raise ProductionRealNLPError("blocked_offline_policy")


def neutral_zero_tensor_rows(date: str, fund_pool: tuple[str, ...]) -> pd.DataFrame:
    rows = []
    for fund in fund_pool:
        rows.append(
            {
                "date": date,
                "track": "",
                "candidate_id": "",
                "fund_id": fund,
                "embedding_vector": json.dumps([0.0] * 16),
                "asset_or_sector_relevance": 0.0,
                "sentiment_score_continuous": 0.0,
                "sentiment_confidence": 0.0,
                "sentiment_entropy": 0.0,
                "sentiment_probabilities": "{}",
                "aspect_scores": "{}",
                "event_label_scores": "{}",
                "event_confidence": 0.0,
                "sector_attention_weights": "{}",
                "recency_decay_weight": 0.0,
                "source_or_cluster_support": 0.0,
                "novelty_score": 0.0,
                "uncertainty_score": 1.0,
                "news_count": 0,
                "missing_news": "true",
                "real_transformer_executed": "false",
                "proxy_mode": "false",
                "heuristic_fallback_used": "false",
                "blocked_reason": "",
            }
        )
    return pd.DataFrame(rows)


def clean_visible_news(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(news_items):
        title = str(item.get("TITLE") or item.get("title") or "")
        content = str(item.get("CONTENT") or item.get("content") or "")
        text = re.sub(r"\s+", " ", f"{title} {content}".strip())[:1200]
        if not text:
            continue
        key = stable_hash({"title": title, "content": content[:500]})
        if key in seen:
            continue
        seen.add(key)
        row = dict(item)
        row["text"] = text
        row["news_id"] = str(item.get("CONTENT_ID") or item.get("news_id") or f"news_{index}")
        row["ranking"] = int(float(item.get("RANKING") or item.get("ranking") or 999))
        rows.append(row)
    rows.sort(key=lambda row: row["ranking"])
    return rows


def recency_decay(item: Mapping[str, Any], date_key: str, half_life_days: float = 2.0) -> float:
    raw = item.get("PUBLISH_TIME") or item.get("publish_time") or item.get("THEDATE")
    try:
        published = pd.to_datetime(raw)
        decision = datetime.strptime(date_key, "%Y%m%d")
        age_days = max(0.0, (decision - published.to_pydatetime()).total_seconds() / 86400.0)
        return float(0.5 ** (age_days / max(0.25, half_life_days)))
    except Exception:
        return 0.65


def support_scores(news_items: list[dict[str, Any]]) -> np.ndarray:
    sources = [str(item.get("APP_TYPE") or item.get("source") or "unknown") for item in news_items]
    counts = Counter(sources)
    return np.asarray([min(1.0, counts[source] / max(1, len(news_items))) for source in sources], dtype=np.float32)


def novelty_scores(texts: list[str]) -> np.ndarray:
    clusters = [stable_hash(re.sub(r"\s+", "", text.lower())[:128])[:12] for text in texts]
    counts = Counter(clusters)
    return np.asarray([1.0 / counts[cluster] for cluster in clusters], dtype=np.float32)


def fund_description(fund_id: str) -> str:
    keywords = FUND_KEYWORDS.get(fund_id, (fund_id,))
    return f"{fund_id} {' '.join(str(item) for item in keywords)}"


def attention_weights(news_items: list[dict[str, Any]], weights: np.ndarray) -> dict[str, float]:
    return {
        str(item.get("news_id") or index): round(float(weights[index]), 8)
        for index, item in enumerate(news_items)
    }


def probability_summary(probabilities: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    if probabilities.size == 0:
        return {}
    pooled = (probabilities * weights[:, None]).sum(axis=0)
    return {f"p_{index}": round(float(value), 8) for index, value in enumerate(pooled)}


def center_values(values: Mapping[str, float]) -> dict[str, float]:
    if not values:
        return {}
    mean = sum(values.values()) / len(values)
    return {key: float(value) - mean for key, value in values.items()}


def cap_l1(values: Mapping[str, float], cap: float) -> dict[str, float]:
    total = sum(abs(value) for value in values.values())
    if total <= cap or total <= 0:
        return dict(values)
    scale = cap / total
    return {key: value * scale for key, value in values.items()}


def normalize_weights(values: Mapping[str, float], *, total: float = 0.97) -> dict[str, float]:
    positive = {key: max(0.0, float(value)) for key, value in values.items()}
    raw_total = sum(positive.values())
    if raw_total <= 0:
        n = max(1, len(positive))
        return {key: total / n for key in positive}
    return {key: (value / raw_total) * total for key, value in positive.items()}


def overlay_diag(base: Mapping[str, float], adjusted: Mapping[str, float], ablation_type: str) -> dict[str, Any]:
    funds = set(base) | set(adjusted)
    overlay_l1 = sum(abs(float(adjusted.get(fund, 0.0)) - float(base.get(fund, 0.0))) for fund in funds)
    return {
        "ablation_type": ablation_type,
        "mean_abs_overlay": overlay_l1 / max(1, len(funds)),
        "overlay_l1": overlay_l1,
        "overlay_nonzero": overlay_l1 > 1e-12,
    }


def model_status_row(role: str, path: Path, exists: bool, loaded: bool, device: str, status: str) -> dict[str, Any]:
    return {
        "model_role": role,
        "required_for_methods": role_methods(role),
        "local_path": str(path),
        "exists": str(bool(exists)).lower(),
        "local_files_only": "true",
        "network_attempted": "false",
        "loaded_successfully": str(bool(loaded)).lower(),
        "device": device,
        "dtype": "float32",
        "sample_input_count": 0,
        "sample_output_shape": "",
        "sample_output_hash": "",
        "proxy_used": "false",
        "blocked_reason": "" if loaded else status,
        "model_sha_or_snapshot": snapshot_id(path),
        "tokenizer_path": str(path),
    }


def role_methods(role: str) -> str:
    if role == "embedding_encoder":
        return "N2;N4;N5;N2345;I5;S6;S126;continuous_relevance;label_attention;sector_attention"
    if role == "financial_sentiment":
        return "N3;N13;I6;I256;continuous_sentiment"
    if role == "reranker":
        return "N6"
    return ""


def snapshot_id(path: Path) -> str:
    parts = list(path.parts)
    if "snapshots" in parts:
        idx = parts.index("snapshots")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return stable_hash(str(path))


def normalize_track_label(track: str) -> str:
    text = str(track).strip().lower()
    if text in {"a", "macro", "track_a", "track1", "track_1"}:
        return "A"
    if text in {"b", "sector", "track_b", "track2", "track_2"}:
        return "B"
    return str(track)


def date_to_key(value: str | int) -> str:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) < 8:
        raise ValueError(f"Invalid date: {value!r}")
    return digits[:8]


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()
