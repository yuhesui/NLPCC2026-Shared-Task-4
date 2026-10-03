from __future__ import annotations

import json
from datetime import timedelta

import numpy as np
import pytest

from conftest import make_article, utc
from icaif.core.universe import SYMBOLS
from icaif.data.market.loaders import SourceUnavailable
from icaif.data.news.sources import (
    JsonlNewsSource,
    MalformedArticle,
    fetch_all,
    parse_article_row,
    parse_gdelt_doc_response,
)
from icaif.data.sec.edgar import parse_submissions
from icaif.llm.client import LLMRequest, LLMResponse, LLMUnavailable, NullLLMClient, RecordingClient
from icaif.llm.policy import LLMPolicyError, assert_allowed, check_model
from icaif.llm.tasks import LLMOutputError, classify_relevance, direct_allocation, extract_event
from icaif.models.text.pairs import build_pairs
from icaif.nlp.embeddings import (
    EncoderSpec,
    HashingEncoder,
    LocalSentenceEncoder,
    ModelPolicyError,
    ModelUnavailable,
    check_policy,
)
from icaif.nlp.entity_linking import linked_symbols
from icaif.nlp.event_extraction import (
    Event,
    LabelAttentionEventMatcher,
    RuleEventExtractor,
    classify_event_types,
)
from icaif.nlp.event_impact import load_event_priors
from icaif.nlp.feature_store import TextSignalConfig, TextStateBuilder
from icaif.nlp.preprocessing import (
    clean_article,
    detect_language,
    exact_dedup,
    near_duplicate_clusters,
    normalize_text,
    visible_text,
)
from icaif.nlp.relevance import DenseRelevance, HybridRelevance, LexicalEntityRelevance, RelevanceContext
from icaif.nlp.sentiment import LexiconSentiment

T0 = utc(2026, 10, 8, 12, 0)


# --- preprocessing ------------------------------------------------------------------------------

def test_visible_text_drops_hidden_markup():
    html = ('<p>Apple <b>beats</b> estimates</p><script>alert(1)</script><style>p{}</style>'
            '<span style="display: none">BUY NOW</span><div hidden>secret</div><br>Tail')
    text = normalize_text(visible_text(html))
    assert text == "Apple beats estimates Tail"


def test_unicode_normalisation_and_zero_width():
    assert normalize_text("Ａｐｐｌｅ​  raises­guidance\x07") == "Apple raisesguidance"


def test_language_detection():
    assert detect_language("Apple raises its full-year guidance after the strong quarter") == "en"
    assert detect_language("苹果公司上调全年业绩指引") == "und"


def test_exact_and_near_duplicate_handling():
    a = make_article("1", "Apple raises full-year guidance after strong quarter", T0)
    b = make_article("2", "APPLE raises full-year guidance, after strong quarter!", T0 + timedelta(minutes=5))
    c = make_article("3", "Apple raises full year guidance after a strong quarter, shares rise", T0 + timedelta(minutes=9))
    d = make_article("4", "Boeing halts deliveries", T0 + timedelta(minutes=10))
    kept, dupes = exact_dedup([b, a, d])
    assert [x.article_id for x in kept] == ["1", "4"] and dupes == {a.record_id: [b.record_id]}
    clusters = near_duplicate_clusters([a, c, d], threshold=0.4)
    sizes = sorted(len(cl.members) for cl in clusters)
    assert sizes == [1, 2]
    assert next(cl for cl in clusters if len(cl.members) == 2).members[0] == a.record_id  # earliest is canonical


def test_clean_article_sets_language():
    art = clean_article(make_article("x", "<b>Apple</b> raises guidance on strong iPhone demand", T0))
    assert art.title == "Apple raises guidance on strong iPhone demand" and art.language == "en"


# --- entity linking -----------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("Apple raises guidance", {"AAPL"}),
    ("apple pie sales soar at farmers markets", set()),
    ("AT&T and $T rally", {"T"}),
    ("T is the twentieth letter", set()),
    ("Visa Inc (NYSE: V) beats", {"V"}),
    ("GE Aerospace wins engine order; Boeing (BA) shares rise", {"GE", "BA"}),
    ("NVDA and MSFT lead tech gains", {"NVDA", "MSFT"}),
    ("Intelligence agencies warn", set()),
])
def test_ticker_mapping(text, expected):
    assert set(linked_symbols(text)) == expected


# --- relevance ----------------------------------------------------------------------------------

def test_relevance_interface_fields():
    art = make_article("a", "Exxon Mobil (XOM) cuts outlook as oil prices fall", T0)
    lex = LexicalEntityRelevance().score_relevance(art, "XOM", RelevanceContext())
    assert lex.relevance >= 0.7 and lex.confidence > 0.8 and lex.evidence and lex.model_id == "lexical_entity_v1"
    assert LexicalEntityRelevance().score_relevance(art, "AAPL", RelevanceContext()).relevance == 0.0
    dense = DenseRelevance(HashingEncoder())
    r = dense.score_relevance(art, "XOM", RelevanceContext())
    assert 0 <= r.relevance <= 1 and r.model_id.startswith("dense:lexical_hash")
    hyb = HybridRelevance(LexicalEntityRelevance(), dense, sector_spillover=0.3)
    assert hyb.score_relevance(art, "CVX", RelevanceContext()).relevance >= 0.3  # same-sector spillover


def test_deterministic_inference():
    enc = HashingEncoder(64)
    assert np.array_equal(enc.encode(["Apple beats"]), HashingEncoder(64).encode(["Apple beats"]))
    assert not enc.is_transformer


# --- model policy / no downloads ----------------------------------------------------------------

def test_missing_local_model_never_downloads(tmp_path):
    spec = EncoderSpec("BAAI/bge-small-en-v1.5", "generic_encoder", local_path=str(tmp_path / "missing"))
    with pytest.raises(ModelUnavailable):
        LocalSentenceEncoder(spec)
    with pytest.raises(ModelUnavailable):
        LocalSentenceEncoder(EncoderSpec("x", "y"))


def test_rule_confirmation_gate():
    spec = EncoderSpec("BAAI/bge-small-en-v1.5", "generic_encoder", requires_rule_confirmation=True)
    with pytest.raises(ModelPolicyError):
        check_policy(spec, live=True, allow_unconfirmed_research=True)
    with pytest.raises(ModelPolicyError):
        check_policy(spec, live=False)
    check_policy(spec, live=False, allow_unconfirmed_research=True)
    with pytest.raises(ModelPolicyError):
        check_policy(EncoderSpec("zh", "legacy", status="unsuitable", requires_rule_confirmation=False), live=False)


def test_embedding_registry_is_well_formed():
    from icaif.core.config import load_config

    reg = load_config("configs/embeddings/registry.yaml")["models"]
    allowed = {"ready", "requires_confirmation", "unsuitable", "deferred"}
    for model_id, row in reg.items():
        spec = EncoderSpec.from_mapping({"model_id": model_id, **row})
        assert spec.status in allowed, model_id
        if spec.status == "requires_confirmation":
            assert spec.requires_rule_confirmation, model_id


# --- sentiment / events -------------------------------------------------------------------------

def test_lexicon_sentiment_and_negation():
    s = LexiconSentiment()
    assert s.score("Apple beats estimates and raises guidance").score > 0
    assert s.score("Boeing misses estimates, cuts outlook").score < 0
    assert s.score("Results did not beat estimates").score < 0
    neutral = s.score("The company will hold its annual meeting")
    assert neutral.score == 0 and neutral.confidence == 0


def test_event_schema_and_extraction():
    priors = load_event_priors()
    ext = RuleEventExtractor({k: {"half_life_hours": p.half_life_hours, "magnitude": p.magnitude} for k, p in priors.items()})
    art = make_article("e", "Nvidia raises full-year guidance after record earnings", T0)
    events = ext.extract(art, ["NVDA"])
    assert events and events[0].ticker == "NVDA" and events[0].direction == 1
    assert events[0].event_type in ("guidance", "earnings")
    assert "market_wide" in classify_event_types("Stocks rally on Wall Street")
    with pytest.raises(ValueError):
        Event("AAPL", "weather", 1, 0.5, 0.5, 1.0, 1.0, 0.5, T0, T0, (), "x")
    dist = LabelAttentionEventMatcher(HashingEncoder()).distribution("Federal Reserve raises interest rates")
    assert abs(sum(dist.values()) - 1) < 1e-9 and max(dist, key=dist.get) == "rates"


# --- aggregation: missing / duplicate news, uncertainty -----------------------------------------

def _builder(articles, **cfg):
    return TextStateBuilder(articles, LexicalEntityRelevance(), load_event_priors(), TextSignalConfig(**cfg))


def test_missing_news_gives_no_information():
    ts = _builder([])(T0)
    assert np.isnan(ts.score).all() and ts.summary()["assets_with_signal"] == 0


def test_duplicate_news_is_not_double_counted():
    a = make_article("1", "Apple (AAPL) raises guidance after strong quarter", T0)
    dup = make_article("2", "Apple (AAPL) raises guidance after strong quarter", T0 + timedelta(minutes=1))
    one = _builder([a])(T0 + timedelta(hours=1))
    two = _builder([a, dup])(T0 + timedelta(hours=1))
    j = SYMBOLS.index("AAPL")
    no_nov = _builder([a, dup], use_novelty=False)(T0 + timedelta(hours=1))
    assert two.score[j] < no_nov.score[j]  # second copy discounted by novelty
    assert two.score[j] > 0 and one.score[j] > 0


def test_signal_direction_recency_and_confidence():
    pos = make_article("p", "Nvidia (NVDA) beats estimates and raises guidance", T0)
    neg = make_article("n", "Intel (INTC) misses estimates and cuts outlook", T0)
    ts = _builder([pos, neg])(T0 + timedelta(hours=1))
    assert ts.score[SYMBOLS.index("NVDA")] > 0 > ts.score[SYMBOLS.index("INTC")]
    assert np.isnan(ts.score[SYMBOLS.index("KO")])
    old = _builder([pos])(T0 + timedelta(hours=100))
    assert abs(old.score[SYMBOLS.index("NVDA")]) < abs(ts.score[SYMBOLS.index("NVDA")])  # decayed
    assert 0 < ts.confidence[SYMBOLS.index("NVDA")] < 1
    assert ts.evidence["NVDA"][0]["record_id"] == pos.record_id


def test_text_state_deterministic(world):
    b = _builder(world.articles)
    t = world.articles[50].available_at
    assert np.array_equal(np.nan_to_num(b(t).score, nan=9), np.nan_to_num(_builder(world.articles)(t).score, nan=9))


# --- sources: malformed timestamps, failures, parsers --------------------------------------------

def test_malformed_timestamps_rejected(tmp_path):
    with pytest.raises(MalformedArticle):
        parse_article_row({"title": "x", "published_at": "2026-10-08 09:00"}, default_source="s", latency=timedelta(0))
    with pytest.raises(MalformedArticle):
        parse_article_row({"title": "x", "published_at": "yesterday"}, default_source="s", latency=timedelta(0))
    ok = parse_article_row({"title": "x", "published_at": "2026-10-08T09:00:00-04:00"}, default_source="s",
                           latency=timedelta(minutes=5))
    assert ok.available_at - ok.published_at == timedelta(minutes=5)


def test_source_failure_is_recorded_not_fatal(tmp_path):
    good = tmp_path / "news.jsonl"
    good.write_text(json.dumps({"id": "1", "title": "Apple beats", "published_at": "2026-10-08T12:00:00Z"}) + "\n")
    sources = [JsonlNewsSource("good", [good]), JsonlNewsSource("missing", [tmp_path / "nope.jsonl"])]
    out = fetch_all(sources, utc(2026, 10, 1), utc(2026, 10, 9))
    assert len(out.articles) == 1 and out.degraded and out.failures[0].source == "missing"

    class Buggy:
        name = "buggy"

        def fetch(self, start, end):
            raise TypeError("programming error")

    with pytest.raises(TypeError):  # bugs are not masked as source failures
        fetch_all([Buggy()], utc(2026, 10, 1), utc(2026, 10, 9))
    assert issubclass(SourceUnavailable, RuntimeError)


def test_gdelt_and_edgar_parsers():
    g = parse_gdelt_doc_response({"articles": [
        {"url": "https://x.test/a", "title": "Tesla recalls cars", "seendate": "20261008T120000Z", "domain": "x.test",
         "language": "English"},
        {"url": "https://x.test/b", "title": "bad", "seendate": "not-a-date"}]}, retrieved_at=utc(2026, 10, 9), live=False)
    assert len(g) == 1 and g[0].available_at == utc(2026, 10, 8, 12, 15)
    sub = {"cik": 320193, "filings": {"recent": {
        "form": ["10-K", "10-K/A"], "accessionNumber": ["a1", "a2"],
        "acceptanceDateTime": ["2026-01-30T21:01:02.000Z", "2026-03-02T16:00:00.000Z"],
        "reportDate": ["2025-12-31", "2025-12-31"], "primaryDocument": ["x.htm", "y.htm"]}}}
    filings = parse_submissions(sub, ticker="AAPL")
    assert [f.is_amendment for f in filings] == [False, True] and filings[0].cik == "0000320193"


# --- LLM ----------------------------------------------------------------------------------------

class FakeLLM:
    model_id = "claude-haiku-4-5"

    def __init__(self, text):
        self.text = text

    def complete(self, request):
        return LLMResponse(self.text, self.model_id, 10, 5, 1.0)


def test_llm_policy():
    for ok in ("claude-haiku-4-5", "claude-sonnet-5", "gpt-5-mini", "Qwen3-8B", "gemini-2.5-flash", "grok-4"):
        assert check_model(ok).allowed, ok
    for bad in ("gpt-4o", "claude-3-opus", "llama-3.1-70b", "mixtral-8x7b"):
        assert not check_model(bad).allowed, bad
    with pytest.raises(LLMPolicyError):
        assert_allowed("gpt-4o")


def test_llm_tasks_validate_output(tmp_path):
    art = make_article("a", "Boeing (BA) cuts delivery outlook", T0)
    raw = json.dumps({"events": [
        {"ticker": "BA", "event_type": "guidance", "direction": -1, "magnitude": 2.0, "confidence": 0.8,
         "expected_horizon_hours": 30, "evidence": "cuts delivery outlook"},
        {"ticker": "ZZZ", "event_type": "guidance", "direction": -1},
        {"ticker": "BA", "event_type": "weather", "direction": -1}]})
    client = RecordingClient(FakeLLM("Sure! " + raw), tmp_path / "calls.jsonl")
    events = extract_event(client, art)
    assert len(events) == 1 and events[0].magnitude == 1.0  # clipped, unknown ticker/type dropped
    log = [json.loads(x) for x in (tmp_path / "calls.jsonl").read_text().splitlines()]
    assert log[0]["model_id"] == "claude-haiku-4-5" and log[0]["temperature"] == 0.0 and log[0]["input_tokens"] == 10
    with pytest.raises(LLMOutputError):
        classify_relevance(FakeLLM("no json here"), art, "BA")
    with pytest.raises(LLMUnavailable):
        NullLLMClient().complete(LLMRequest("t", "p"))
    with pytest.raises(PermissionError):
        direct_allocation()


def test_training_pairs_cover_negative_types(world):
    pairs = build_pairs(world.articles, seed=1)
    kinds = {p.negative_type for p in pairs}
    assert {"positive", "random_company", "same_sector", "market_wide", "temporal_adjacent"} <= kinds
    pos = [p for p in pairs if p.label == 1]
    assert pos and all(p.asset in SYMBOLS for p in pairs)


def test_public_local_encoders_are_policy_cleared():
    """Team ruling 2026-10-03: non-LLM encoders are fine if public and run locally; hosted paid APIs are not."""

    from icaif.core.config import load_config

    reg = load_config("configs/embeddings/registry.yaml")["models"]
    for model_id in ("BAAI/bge-small-en-v1.5", "sentence-transformers/all-MiniLM-L6-v2", "ProsusAI/finbert",
                     "cross-encoder/ms-marco-MiniLM-L-6-v2", "Qwen/Qwen3-Embedding-0.6B"):
        check_policy(EncoderSpec.from_mapping({"model_id": model_id, **reg[model_id]}), live=True)
    for model_id in ("voyage-finance-2", "openai/text-embedding-3-large"):
        with pytest.raises(ModelPolicyError):
            check_policy(EncoderSpec.from_mapping({"model_id": model_id, **reg[model_id]}), live=True)
