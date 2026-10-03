"""Text preprocessing: visible-text extraction, normalisation, dedup, clustering.

Deterministic, dependency-free (stdlib only). Hash functions are SHA/BLAKE2
based so results are identical across processes (Python's ``hash`` is salted).
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import timedelta
from html.parser import HTMLParser

from icaif.core.schemas import Article

_ZERO_WIDTH = re.compile("[​‌‍⁠﻿­᠎‪-‮⁦-⁩]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WS = re.compile(r"\s+")
_HIDDEN_TAGS = {"script", "style", "noscript", "template", "head", "svg", "iframe"}


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0
        self._hidden_stack: list[bool] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        style = " ".join((v or "") for k, v in attrs if k == "style").replace(" ", "").lower()
        hidden = tag in _HIDDEN_TAGS or "display:none" in style or "visibility:hidden" in style or any(
            k == "hidden" or (k == "aria-hidden" and v == "true") for k, v in attrs)
        if tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4"):
            self.parts.append(" ")
        if tag in ("br", "img", "hr", "meta", "link", "input"):
            return  # void elements: no end tag
        self._hidden_stack.append(hidden)
        if hidden:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if self._hidden_stack and self._hidden_stack.pop():
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if self._skip == 0:
            self.parts.append(data)


def visible_text(html: str) -> str:
    """Strip markup; drop script/style and visibly hidden elements."""

    if "<" not in html:
        return html
    parser = _VisibleText()
    parser.feed(html)
    parser.close()
    return "".join(parser.parts)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _ZERO_WIDTH.sub("", text)
    text = _CONTROL.sub(" ", text)
    return _WS.sub(" ", text).strip()


_EN_STOP = frozenset(["the", "a", "an", "and", "of", "to", "in", "for", "on", "with", "as", "by", "at", "from", "is", "are", "was", "were", "be", "has", "have", "its", "it", "this", "that"])


def detect_language(text: str) -> str:
    """Cheap heuristic: 'en' if mostly ASCII letters with English stopwords,
    'und' otherwise. Replace with a proper detector in research configs."""

    letters = [c for c in text if c.isalpha()]
    if len(letters) < 10:
        return "und"
    ascii_ratio = sum(c.isascii() for c in letters) / len(letters)
    words = re.findall(r"[a-z]+", text.lower())
    stop_ratio = sum(w in _EN_STOP for w in words) / max(1, len(words))
    if ascii_ratio > 0.9 and (stop_ratio > 0.05 or len(words) < 15):
        return "en"
    return "und"


def clean_article(article: Article) -> Article:
    title = normalize_text(visible_text(article.title))
    body = normalize_text(visible_text(article.body))
    lang = article.language if article.language not in ("", "und") else detect_language(f"{title} {body}")
    return replace(article, title=title, body=body, language=lang)


def text_fingerprint(text: str) -> str:
    canon = re.sub(r"[^a-z0-9]+", " ", normalize_text(text).lower()).strip()
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def exact_dedup(articles: Sequence[Article]) -> tuple[list[Article], dict[str, list[str]]]:
    """Keep the earliest-available copy of identical normalised text."""

    groups: dict[str, list[Article]] = {}
    for a in sorted(articles, key=lambda x: (x.available_at, x.record_id)):
        groups.setdefault(text_fingerprint(a.text), []).append(a)
    kept = [g[0] for g in groups.values()]
    dupes = {g[0].record_id: [x.record_id for x in g[1:]] for g in groups.values() if len(g) > 1}
    return sorted(kept, key=lambda x: x.available_at), dupes


def shingles(text: str, k: int = 2) -> set[str]:
    """Word k-shingles. k=2 suits headline-length texts; always compare sets
    built with the same k."""

    tokens = re.findall(r"[a-z0-9]+", normalize_text(text).lower())
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i:i + k]) for i in range(len(tokens) - k + 1)}


def minhash_signature(items: set[str], num_perm: int = 64) -> tuple[int, ...]:
    if not items:
        return tuple([2**64 - 1] * num_perm)
    sig = []
    for seed in range(num_perm):
        salt = seed.to_bytes(8, "little")
        sig.append(min(int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8, salt=salt[:8]).digest(), "little")
                       for s in items))
    return tuple(sig)


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    members: tuple[str, ...]  # record ids, first = earliest available (canonical)
    first_available: str


def near_duplicate_clusters(articles: Sequence[Article], *, threshold: float = 0.6,
                            window: timedelta = timedelta(hours=48)) -> list[Cluster]:
    """Greedy clustering by shingle Jaccard within a time window.

    Exact-Jaccard on candidates (30 assets x a few hundred articles per window
    is small); MinHash is available for scaling (``minhash_signature``).
    """

    ordered = sorted(articles, key=lambda x: (x.available_at, x.record_id))
    sh = [shingles(a.text) for a in ordered]
    assigned = [-1] * len(ordered)
    clusters: list[list[int]] = []
    for i, a in enumerate(ordered):
        best, best_sim = -1, threshold
        for c_idx, members in enumerate(clusters):
            head = members[0]
            if a.available_at - ordered[head].available_at > window:
                continue
            sim = jaccard(sh[i], sh[head])
            if sim >= best_sim:
                best, best_sim = c_idx, sim
        if best >= 0:
            clusters[best].append(i)
            assigned[i] = best
        else:
            clusters.append([i])
            assigned[i] = len(clusters) - 1
    out = []
    for members in clusters:
        ids = tuple(ordered[m].record_id for m in members)
        cid = hashlib.sha256("|".join(ids).encode()).hexdigest()[:12]
        out.append(Cluster(cid, ids, ordered[members[0]].available_at.isoformat()))
    return out


def novelty_by_record(clusters: Sequence[Cluster]) -> dict[str, float]:
    """Canonical (first) member gets novelty 1, later copies 1/(position+1)."""

    out: dict[str, float] = {}
    for c in clusters:
        for pos, rid in enumerate(c.members):
            out[rid] = 1.0 / (pos + 1)
    return out
