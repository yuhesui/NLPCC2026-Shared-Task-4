"""Rule-based sentiment classifier."""

from __future__ import annotations

from nlpcc.stage1_news.schema import NormalizedNewsItem, SentimentSignal


POSITIVE_KEYWORDS = (
    "support",
    "stimulus",
    "growth",
    "cut rates",
    "rate cut",
    "approval",
    "recovery",
    "profit",
    "beat",
    "支持",
    "刺激",
    "增长",
    "降息",
    "复苏",
    "利好",
    "盈利",
)
NEGATIVE_KEYWORDS = (
    "risk",
    "default",
    "crackdown",
    "decline",
    "loss",
    "inflation",
    "sanction",
    "tighten",
    "风险",
    "违约",
    "下滑",
    "亏损",
    "通胀",
    "制裁",
    "收紧",
    "利空",
)


def classify_sentiment(item: NormalizedNewsItem) -> SentimentSignal:
    text = item.text.lower()
    positive_hits = tuple(keyword for keyword in POSITIVE_KEYWORDS if keyword.lower() in text)
    negative_hits = tuple(keyword for keyword in NEGATIVE_KEYWORDS if keyword.lower() in text)
    raw_score = len(positive_hits) - len(negative_hits)
    if raw_score > 0:
        label = "positive"
    elif raw_score < 0:
        label = "negative"
    else:
        label = "neutral"
    confidence = min(1.0, 0.45 + 0.15 * (len(positive_hits) + len(negative_hits)))
    score = max(-1.0, min(1.0, raw_score / 3.0))
    return SentimentSignal(
        news_id=item.news_id,
        label=label,
        score=score,
        confidence=confidence,
        evidence=positive_hits + negative_hits,
    )
