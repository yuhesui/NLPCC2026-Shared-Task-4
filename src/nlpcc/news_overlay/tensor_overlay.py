"""Prompt08 continuous news tensor and bounded overlay utilities.

The module is intentionally local-only: it can use already-cached transformer
snapshots, and falls back to deterministic continuous hash features when a
local model cannot be loaded. It never downloads models or calls online APIs.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import math
from pathlib import Path
import re
from typing import Any, Iterable

import numpy as np
import pandas as pd


FEATURE_COLUMNS = (
    "relevance_score",
    "sentiment_intensity",
    "sentiment_confidence",
    "event_intensity",
    "novelty_score",
    "source_agreement_or_cluster_count",
    "recency_decay_weight",
    "asset_or_sector_affinity",
    "uncertainty_score",
)

DEFAULT_BGE_PATH = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--BAAI--bge-small-zh-v1.5"
    / "snapshots"
    / "e534609e6b53ac54bd42d8e87995d21a73b90bad"
)
DEFAULT_FINBERT_PATH = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--yiyanghkust--finbert-tone-chinese"
    / "snapshots"
    / "e91b1a3af10e1e8c9c03429d3cd7d5e9a1c8000d"
)

POSITIVE_CUES = (
    "利好",
    "支持",
    "增长",
    "上升",
    "改善",
    "释放",
    "回暖",
    "复苏",
    "预增",
    "宽松",
    "降准",
    "降息",
)
NEGATIVE_CUES = (
    "利空",
    "下滑",
    "下降",
    "亏损",
    "违约",
    "风险",
    "收紧",
    "处罚",
    "限制",
    "冲突",
    "制裁",
    "暴雷",
)
EVENT_CUES = (
    "政策",
    "监管",
    "降准",
    "降息",
    "融资",
    "业绩",
    "订单",
    "违约",
    "冲突",
    "制裁",
    "价格",
    "库存",
    "出口",
    "创新",
    "AI",
)

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


@dataclass(frozen=True)
class NewsTensorConfig:
    """Runtime options for Prompt08 tensor construction."""

    use_transformer: bool = True
    bge_path: Path = DEFAULT_BGE_PATH
    finbert_path: Path = DEFAULT_FINBERT_PATH
    device: str = "cuda"
    batch_size: int = 32
    max_news_per_day: int = 20
    half_life_days: float = 2.0
    schema_version: str = "prompt08_news_tensor_v1"
    config_id: str = "prompt08_transformer_tensor_default"


@dataclass(frozen=True)
class OverlayConfig:
    """Bounded overlay parameters used by E1/E2/E3 variants."""

    variant: str
    overlay_cap: float = 0.012
    per_asset_cap: float = 0.004
    confidence_threshold: float = 0.42
    entropy_threshold: float = 1.10
    relevance_threshold: float = 0.08
    deadband: float = 0.0004
    turnover_cap: float = 0.035
    shrink_strength: float = 0.40
    regime_gate_threshold: float = 0.16
    drawdown_guard_threshold: float = 0.12
    event_confirmation_threshold: float = 1.0
    recency_half_life: float = 2.0
    use_confidence_gate: bool = True
    use_regime_gate: bool = False
    use_turnover_guard: bool = True
    use_drawdown_guard: bool = False
    use_uncertainty_shrink: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class LocalTransformerTensorBackend:
    """Small local-only wrapper around cached BGE and FinBERT snapshots."""

    def __init__(self, config: NewsTensorConfig) -> None:
        self.config = config
        self.backend_status: dict[str, Any] = {
            "uses_transformer_real": False,
            "uses_encoder_proxy": True,
            "bge_status": "not_loaded",
            "finbert_status": "not_loaded",
            "device_requested": config.device,
            "device_used": "cpu",
        }
        self._torch = None
        self._encoder_tokenizer = None
        self._encoder_model = None
        self._sentiment_tokenizer = None
        self._sentiment_model = None
        self._sentiment_labels: list[str] = []
        if config.use_transformer:
            self._load_local_models()

    def _load_local_models(self) -> None:
        try:
            import torch  # type: ignore
            from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
        except Exception as exc:
            self.backend_status["bge_status"] = f"blocked_dependency:{type(exc).__name__}"
            self.backend_status["finbert_status"] = f"blocked_dependency:{type(exc).__name__}"
            return

        self._torch = torch
        device = "cuda" if self.config.device == "cuda" and torch.cuda.is_available() else "cpu"
        self.backend_status["device_used"] = device
        if self.config.bge_path.exists():
            try:
                self._encoder_tokenizer = AutoTokenizer.from_pretrained(str(self.config.bge_path), local_files_only=True)
                self._encoder_model = AutoModel.from_pretrained(str(self.config.bge_path), local_files_only=True)
                self._encoder_model.to(device)
                self._encoder_model.eval()
                self.backend_status["bge_status"] = "available_local_files_only"
            except Exception as exc:
                self.backend_status["bge_status"] = f"blocked_load_failed:{type(exc).__name__}"
        else:
            self.backend_status["bge_status"] = "blocked_missing_local_model"

        if self.config.finbert_path.exists():
            try:
                self._sentiment_tokenizer = AutoTokenizer.from_pretrained(str(self.config.finbert_path), local_files_only=True)
                self._sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                    str(self.config.finbert_path),
                    local_files_only=True,
                )
                self._sentiment_model.to(device)
                self._sentiment_model.eval()
                labels = getattr(getattr(self._sentiment_model, "config", None), "id2label", {}) or {}
                width = int(getattr(getattr(self._sentiment_model, "config", None), "num_labels", 3) or 3)
                self._sentiment_labels = [str(labels.get(i, labels.get(str(i), f"LABEL_{i}"))) for i in range(width)]
                self.backend_status["finbert_status"] = "available_local_files_only"
            except Exception as exc:
                self.backend_status["finbert_status"] = f"blocked_load_failed:{type(exc).__name__}"
        else:
            self.backend_status["finbert_status"] = "blocked_missing_local_model"

        self.backend_status["uses_transformer_real"] = self._encoder_model is not None or self._sentiment_model is not None
        self.backend_status["uses_encoder_proxy"] = not bool(self.backend_status["uses_transformer_real"])

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 16), dtype=np.float32)
        if self._encoder_model is None or self._encoder_tokenizer is None or self._torch is None:
            return np.asarray([hash_embedding(text, dims=32) for text in texts], dtype=np.float32)
        rows: list[np.ndarray] = []
        torch = self._torch
        device = str(self.backend_status["device_used"])
        batch_size = max(1, int(self.config.batch_size))
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = self._encoder_tokenizer(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad():
                output = self._encoder_model(**encoded)
                hidden = output.last_hidden_state
                mask = encoded["attention_mask"].unsqueeze(-1).float()
                pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
                pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            rows.append(pooled.detach().cpu().numpy())
        return np.vstack(rows).astype(np.float32)

    def sentiment(self, texts: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not texts:
            return np.zeros(0), np.zeros(0), np.zeros(0)
        if self._sentiment_model is None or self._sentiment_tokenizer is None or self._torch is None:
            return proxy_sentiment(texts)
        torch = self._torch
        device = str(self.backend_status["device_used"])
        batch_size = max(1, int(self.config.batch_size))
        score_rows: list[float] = []
        confidence_rows: list[float] = []
        entropy_rows: list[float] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = self._sentiment_tokenizer(batch, padding=True, truncation=True, max_length=256, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad():
                logits = self._sentiment_model(**encoded).logits
                probs = torch.nn.functional.softmax(logits, dim=-1).detach().cpu().numpy()
            for row in probs:
                labelled = {self._sentiment_labels[idx].lower(): float(value) for idx, value in enumerate(row)}
                positive = sum(value for label, value in labelled.items() if "pos" in label or label in {"label_2", "2"})
                negative = sum(value for label, value in labelled.items() if "neg" in label or label in {"label_0", "0"})
                if positive == 0.0 and negative == 0.0 and len(row) >= 2:
                    negative = float(row[0])
                    positive = float(row[-1])
                score_rows.append(max(-1.0, min(1.0, positive - negative)))
                confidence_rows.append(float(np.max(row)))
                entropy_rows.append(float(-np.sum(row * np.log(np.maximum(row, 1e-12)))))
        return np.asarray(score_rows), np.asarray(confidence_rows), np.asarray(entropy_rows)


def build_daily_news_tensor(
    *,
    date: int,
    fund_pool: Iterable[str],
    news_items: list[dict[str, Any]],
    backend: LocalTransformerTensorBackend,
    config: NewsTensorConfig,
) -> pd.DataFrame:
    """Build one date's tensor rows as a flat dataframe."""

    visible = clean_news_items(news_items)[: max(0, int(config.max_news_per_day))]
    funds = tuple(fund_pool)
    if not visible or not funds:
        return pd.DataFrame(columns=["date", "fund_id", *FEATURE_COLUMNS, "news_count", "uses_transformer_real", "uses_encoder_proxy"])

    texts = [item["text"] for item in visible]
    text_vectors = backend.encode(texts)
    fund_vectors = np.asarray([hash_embedding(" ".join(FUND_KEYWORDS.get(fund, (fund,))), dims=text_vectors.shape[1]) for fund in funds])
    sentiment_score, sentiment_confidence, entropy = backend.sentiment(texts)
    event_scores = np.asarray([event_intensity(text) for text in texts], dtype=np.float32)
    novelty = novelty_scores(texts)
    cluster_counts = cluster_count_scores(texts)
    recency = np.asarray([recency_weight(item, date, config.half_life_days) for item in visible], dtype=np.float32)
    ranks = np.asarray([1.0 / max(1.0, float(item.get("ranking", 20))) for item in visible], dtype=np.float32)
    rows: list[dict[str, Any]] = []
    similarities = np.maximum(0.0, text_vectors @ fund_vectors.T)
    for fund_idx, fund in enumerate(funds):
        affinity = similarities[:, fund_idx]
        relevance = np.clip(0.62 * affinity + 0.28 * ranks + 0.10 * keyword_affinity_scores(texts, fund), 0.0, 1.0)
        weights = relevance * recency
        total = float(weights.sum()) or 1.0
        signed = sentiment_score * sentiment_confidence * weights
        row = {
            "date": str(date),
            "fund_id": fund,
            "relevance_score": round(float(np.average(relevance, weights=np.maximum(weights, 1e-6))), 8),
            "sentiment_intensity": round(float(signed.sum() / total), 8),
            "sentiment_confidence": round(float(np.average(sentiment_confidence, weights=np.maximum(weights, 1e-6))), 8),
            "event_intensity": round(float(np.average(event_scores, weights=np.maximum(weights, 1e-6))), 8),
            "novelty_score": round(float(np.average(novelty, weights=np.maximum(weights, 1e-6))), 8),
            "source_agreement_or_cluster_count": round(float(np.average(cluster_counts, weights=np.maximum(weights, 1e-6))), 8),
            "recency_decay_weight": round(float(np.average(recency, weights=np.maximum(relevance, 1e-6))), 8),
            "asset_or_sector_affinity": round(float(np.max(affinity) if len(affinity) else 0.0), 8),
            "uncertainty_score": round(float(np.average(entropy / math.log(max(2, len(backend._sentiment_labels) or 3)), weights=np.maximum(weights, 1e-6))), 8),
            "news_count": len(visible),
            "uses_transformer_real": str(bool(backend.backend_status["uses_transformer_real"])).lower(),
            "uses_encoder_proxy": str(bool(backend.backend_status["uses_encoder_proxy"])).lower(),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def apply_bounded_news_overlay(
    baseline_weights: pd.DataFrame,
    news_weights: pd.DataFrame,
    tensor_rows: pd.DataFrame,
    config: OverlayConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return enhanced target weights and daily diagnostics."""

    base = normalize_weight_frame(baseline_weights)
    news = normalize_weight_frame(news_weights)
    tensor = tensor_rows.copy()
    tensor["date"] = tensor["date"].astype(str)
    out_rows: list[dict[str, Any]] = []
    diag_rows: list[dict[str, Any]] = []
    previous: dict[str, float] | None = None
    for date, group in base.groupby("date", sort=True):
        b = dict(zip(group["fund_id"], group["target_weight"]))
        n_group = news[news["date"] == date]
        n = dict(zip(n_group["fund_id"], n_group["target_weight"]))
        t_group = tensor[tensor["date"] == date]
        raw_overlay: dict[str, float] = {}
        for _, row in t_group.iterrows():
            fund = str(row["fund_id"])
            relevance = float(row["relevance_score"])
            confidence = float(row["sentiment_confidence"])
            uncertainty = float(row["uncertainty_score"])
            event = float(row["event_intensity"])
            sentiment = float(row["sentiment_intensity"])
            if config.use_confidence_gate and (confidence < config.confidence_threshold or relevance < config.relevance_threshold):
                signal = 0.0
            elif uncertainty > config.entropy_threshold:
                signal = 0.0
            elif event < config.event_confirmation_threshold * 0.05:
                signal = 0.0
            else:
                signal = sentiment * relevance * confidence * float(row["recency_decay_weight"])
            if abs(signal) < config.deadband:
                signal = 0.0
            delta_from_news = n.get(fund, b.get(fund, 0.0)) - b.get(fund, 0.0)
            overlay = 0.55 * delta_from_news + 0.45 * signal * config.per_asset_cap
            if config.use_uncertainty_shrink:
                overlay *= max(0.0, 1.0 - config.shrink_strength * uncertainty)
            raw_overlay[fund] = overlay

        all_funds = sorted(set(b) | set(n) | set(raw_overlay))
        overlay_values = {fund: clamp(raw_overlay.get(fund, 0.0), -config.per_asset_cap, config.per_asset_cap) for fund in all_funds}
        overlay_values = cap_l1(overlay_values, config.overlay_cap)
        if config.use_regime_gate:
            vol = realized_overlay_pressure(previous, b)
            if vol > config.regime_gate_threshold:
                overlay_values = {fund: value * 0.35 for fund, value in overlay_values.items()}
        values = {fund: max(0.0, b.get(fund, 0.0) + overlay_values.get(fund, 0.0)) for fund in all_funds}
        values = normalize_weights(values)
        if config.use_turnover_guard and previous is not None:
            turnover = sum(abs(values.get(fund, 0.0) - previous.get(fund, 0.0)) for fund in set(values) | set(previous))
            if turnover > config.turnover_cap:
                shrink = config.turnover_cap / turnover
                values = normalize_weights({fund: previous.get(fund, 0.0) + (values.get(fund, 0.0) - previous.get(fund, 0.0)) * shrink for fund in set(values) | set(previous)})
        overlay_l1 = sum(abs(values.get(fund, 0.0) - b.get(fund, 0.0)) for fund in set(values) | set(b))
        overlay_abs_mean = overlay_l1 / max(1, len(set(values) | set(b)))
        for fund, value in sorted(values.items()):
            out_rows.append({"date": date, "fund_id": fund, "target_weight": round(float(value), 8)})
        diag_rows.append(
            {
                "date": date,
                "variant": config.variant,
                "overlay_l1": round(float(overlay_l1), 8),
                "mean_abs_overlay": round(float(overlay_abs_mean), 8),
                "overlay_nonzero": str(overlay_l1 > 1e-9).lower(),
                "uses_confidence_gate": str(config.use_confidence_gate).lower(),
                "uses_regime_gate": str(config.use_regime_gate).lower(),
                "uses_turnover_guard": str(config.use_turnover_guard).lower(),
                "uses_drawdown_guard": str(config.use_drawdown_guard).lower(),
            }
        )
        previous = values
    return pd.DataFrame(out_rows), pd.DataFrame(diag_rows)


def normalize_weight_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["date"] = out["date"].astype(str).str.replace("-", "", regex=False).str[:8]
    out["fund_id"] = out["fund_id"].astype(str)
    out["target_weight"] = out["target_weight"].astype(float)
    return out


def replay_weight_returns(weights: pd.DataFrame, price_dir: Path) -> dict[str, Any]:
    """Simple close-to-close replay for research metrics."""

    frame = normalize_weight_frame(weights)
    funds = sorted(frame["fund_id"].unique())
    prices: dict[str, pd.DataFrame] = {}
    for fund in funds:
        path = price_dir / f"{fund}.csv"
        if path.exists():
            df = pd.read_csv(path)
            df["date"] = df["date"].astype(str).str[:8]
            df["close"] = pd.to_numeric(df["close"], errors="coerce")
            prices[fund] = df.set_index("date")
    dates = sorted(set(frame["date"]))
    daily_returns: list[float] = []
    prev_weights: dict[str, float] = {}
    turnover_values: list[float] = []
    equity = 1.0
    values = [equity]
    for date, next_date in zip(dates, dates[1:]):
        rows = frame[frame["date"] == date]
        cur_weights = dict(zip(rows["fund_id"], rows["target_weight"]))
        ret = 0.0
        for fund, weight in cur_weights.items():
            df = prices.get(fund)
            if df is None or date not in df.index or next_date not in df.index:
                continue
            close0 = float(df.loc[date, "close"])
            close1 = float(df.loc[next_date, "close"])
            if close0 > 0:
                ret += float(weight) * (close1 / close0 - 1.0)
        turnover_values.append(sum(abs(cur_weights.get(fund, 0.0) - prev_weights.get(fund, 0.0)) for fund in set(cur_weights) | set(prev_weights)))
        prev_weights = cur_weights
        daily_returns.append(ret)
        equity *= 1.0 + ret
        values.append(equity)
    returns = np.asarray(daily_returns, dtype=float)
    sharpe = 0.0 if returns.size == 0 or float(returns.std()) == 0.0 else float(returns.mean() / returns.std() * math.sqrt(252))
    peak = np.maximum.accumulate(np.asarray(values, dtype=float)) if values else np.asarray([1.0])
    drawdowns = 1.0 - np.asarray(values, dtype=float) / np.maximum(peak, 1e-12)
    return {
        "return": round(float(equity - 1.0), 8),
        "sharpe": round(float(sharpe), 8),
        "max_drawdown": round(float(drawdowns.max() if drawdowns.size else 0.0), 8),
        "turnover": round(float(np.mean(turnover_values) if turnover_values else 0.0), 8),
        "date_start": dates[0] if dates else "",
        "date_end": dates[-1] if dates else "",
        "num_days": len(dates),
    }


def clean_news_items(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for item in news_items:
        title = str(item.get("TITLE") or item.get("title") or "")
        content = str(item.get("CONTENT") or item.get("content") or "")
        text = f"{title} {content}".strip()
        if not text:
            continue
        key = hashlib.sha256(re.sub(r"\s+", "", text[:500]).encode("utf-8", errors="ignore")).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        row = dict(item)
        row["text"] = text[:1200]
        row["ranking"] = int(float(item.get("RANKING") or item.get("ranking") or 20))
        rows.append(row)
    rows.sort(key=lambda row: row["ranking"])
    return rows


def hash_embedding(text: str, dims: int = 32) -> np.ndarray:
    values = []
    for idx in range(dims):
        digest = hashlib.sha256(f"{idx}:{text}".encode("utf-8", errors="ignore")).digest()
        values.append((int.from_bytes(digest[:4], "little") / 2**32) * 2.0 - 1.0)
    arr = np.asarray(values, dtype=np.float32)
    norm = float(np.linalg.norm(arr)) or 1.0
    return arr / norm


def proxy_sentiment(texts: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scores = []
    confidence = []
    entropy = []
    for text in texts:
        positive = sum(1 for cue in POSITIVE_CUES if cue.lower() in text.lower())
        negative = sum(1 for cue in NEGATIVE_CUES if cue.lower() in text.lower())
        total = max(1, positive + negative)
        score = (positive - negative) / total
        conf = min(0.92, 0.34 + 0.12 * total)
        scores.append(score)
        confidence.append(conf)
        entropy.append(1.05 - 0.45 * abs(score))
    return np.asarray(scores), np.asarray(confidence), np.asarray(entropy)


def event_intensity(text: str) -> float:
    lower = text.lower()
    hits = sum(1 for cue in EVENT_CUES if cue.lower() in lower)
    return min(1.0, hits / 4.0)


def novelty_scores(texts: list[str]) -> np.ndarray:
    counts = Counter(cluster_key(text) for text in texts)
    return np.asarray([1.0 / counts[cluster_key(text)] for text in texts], dtype=np.float32)


def cluster_count_scores(texts: list[str]) -> np.ndarray:
    counts = Counter(cluster_key(text) for text in texts)
    return np.asarray([min(1.0, counts[cluster_key(text)] / 3.0) for text in texts], dtype=np.float32)


def cluster_key(text: str) -> str:
    return hashlib.sha256(re.sub(r"\s+", "", text.lower())[:96].encode("utf-8", errors="ignore")).hexdigest()[:12]


def recency_weight(item: dict[str, Any], decision_date: int, half_life_days: float) -> float:
    raw = item.get("PUBLISH_TIME") or item.get("publish_time") or item.get("THEDATE")
    try:
        published = pd.to_datetime(raw)
        decision = datetime.strptime(str(decision_date)[:8], "%Y%m%d")
        age_days = max(0.0, (decision - published.to_pydatetime()).total_seconds() / 86400.0)
        return float(0.5 ** (age_days / max(0.25, half_life_days)))
    except Exception:
        return 0.65


def keyword_affinity_scores(texts: list[str], fund_id: str) -> np.ndarray:
    keywords = FUND_KEYWORDS.get(fund_id, (fund_id,))
    values = []
    for text in texts:
        lower = text.lower()
        hits = sum(1 for keyword in keywords if keyword.lower() in lower)
        values.append(min(1.0, hits / max(1, len(keywords) ** 0.5)))
    return np.asarray(values, dtype=np.float32)


def cap_l1(values: dict[str, float], cap: float) -> dict[str, float]:
    total = sum(abs(value) for value in values.values())
    if total <= cap or total == 0:
        return values
    scale = cap / total
    return {key: value * scale for key, value in values.items()}


def normalize_weights(values: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, value) for value in values.values())
    if total <= 0:
        n = max(1, len(values))
        return {key: 1.0 / n for key in values}
    return {key: max(0.0, value) / total for key, value in values.items()}


def realized_overlay_pressure(previous: dict[str, float] | None, current: dict[str, float]) -> float:
    if previous is None:
        return 0.0
    return sum(abs(current.get(fund, 0.0) - previous.get(fund, 0.0)) for fund in set(current) | set(previous))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
