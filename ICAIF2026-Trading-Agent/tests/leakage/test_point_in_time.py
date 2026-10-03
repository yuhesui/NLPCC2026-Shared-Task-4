"""Point-in-time guarantees: nothing with available_at > decision_time can be used."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timedelta

import numpy as np
import pytest

from conftest import make_article, make_bar, utc
from icaif.backtest.walk_forward import Segment, TemporalSplit, purge
from icaif.core.leakage_guard import (
    LeakageViolation,
    assert_labels_before,
    assert_model_cutoff,
    assert_visible,
)
from icaif.core.schemas import Filing, MacroObservation, MarketBar, Provenance
from icaif.core.time import NaiveTimestampError, et_datetime, parse_timestamp
from icaif.core.universe import SYMBOLS
from icaif.data.macro.alfred import parse_alfred_observations
from icaif.data.market.panel import MarketPanel
from icaif.data.point_in_time import FilingStore, MacroStore, PITStore
from icaif.nlp.recency import age_hours


def _panel(day: date, minutes: int, delay_s: int = 60) -> MarketPanel:
    bars = []
    start = et_datetime(day, "09:30")
    close = et_datetime(day, "16:00")
    t = start
    while t < close:
        span = min(minutes, int((close - t).total_seconds() // 60))
        for s in SYMBOLS:
            bars.append(make_bar(s, t, span, delay_s=delay_s))
        t += timedelta(minutes=span)
    return MarketPanel.from_bars(bars, bar_minutes=minutes, synthetic=True)


# --- intraday bars -------------------------------------------------------------------------------

def test_partial_intraday_bar_never_visible():
    day = date(2026, 10, 8)
    panel = _panel(day, 60)
    r2_as_of = et_datetime(day, "10:20")  # R2 deadline 10:25; the 09:30-10:30 bar is incomplete
    view = panel.as_of(r2_as_of)
    assert view.n_bars == 0
    later = panel.as_of(et_datetime(day, "10:31"))  # 10:30 bar end + 60s availability delay
    assert later.n_bars == 1 and later.last_bar_end == et_datetime(day, "10:30")


def test_thirty_minute_bars_reduce_staleness():
    day = date(2026, 10, 8)
    view = _panel(day, 30).as_of(et_datetime(day, "10:20"))
    assert view.last_bar_end == et_datetime(day, "10:00")
    assert all(a <= view.as_of for a in view.panel.available_at[: view.stop])


def test_bar_cannot_be_available_before_it_completes():
    start = et_datetime(date(2026, 10, 8), "09:30")
    with pytest.raises(ValueError):
        MarketBar("AAPL", start, start + timedelta(minutes=30), 1, 1, 1, 1, 1, start + timedelta(minutes=29),
                  Provenance("t", "x", "h"))


def test_daily_bar_visible_only_after_close():
    day = date(2026, 10, 8)
    bars = [make_bar(s, et_datetime(day, "09:30"), 390) for s in SYMBOLS]
    panel = MarketPanel.from_bars(bars, bar_minutes=390, synthetic=True)
    assert panel.as_of(et_datetime(day, "15:59")).n_bars == 0
    assert panel.as_of(et_datetime(day, "16:01")).n_bars == 1


def test_future_price_perturbation_does_not_change_earlier_decision(world):
    """Poison every bar after t: decisions with AS_OF < t must be identical."""

    from icaif.features.momentum import multi_horizon_score

    panel = world.panel
    cut = len(panel.ends) - 30
    as_of = panel.available_at[cut - 1]
    poisoned = replace(panel, close=np.where(np.arange(len(panel.ends))[:, None] >= cut, panel.close * 5.0, panel.close))
    a = multi_horizon_score(panel.as_of(as_of), {"1d": 1.0, "5d": 1.0})
    b = multi_horizon_score(poisoned.as_of(as_of), {"1d": 1.0, "5d": 1.0})
    assert np.array_equal(a, b)


# --- news ---------------------------------------------------------------------------------------

def test_future_article_rejected():
    t0 = utc(2026, 10, 8, 13, 0)
    early = make_article("a", "Apple raises guidance", t0)
    late = make_article("b", "Apple cuts guidance", t0 + timedelta(hours=2))
    store = PITStore([early, late])
    assert [a.article_id for a in store.as_of(t0 + timedelta(hours=1))] == ["a"]
    with pytest.raises(LeakageViolation):
        assert_visible([late], t0 + timedelta(hours=1))


def test_availability_cannot_precede_publication():
    t0 = utc(2026, 10, 8, 13, 0)
    with pytest.raises(ValueError):
        make_article("x", "t", t0, delay_s=-1)


def test_publication_exactly_at_cutoff_is_visible_but_one_microsecond_later_is_not():
    t0 = utc(2026, 10, 8, 13, 0)
    art = make_article("a", "x", t0, delay_s=0)
    assert PITStore([art]).as_of(t0)
    assert not PITStore([art]).as_of(t0 - timedelta(microseconds=1))


# --- SEC amendments -----------------------------------------------------------------------------

def test_amended_filing_does_not_leak_backwards():
    prov = Provenance("sec_edgar", "x", "h")
    original = Filing("0000320193", "AAPL", "10-K", "0001", utc(2026, 1, 30, 21, 0), replace(prov, source_id="0001"))
    amended = Filing("0000320193", "AAPL", "10-K/A", "0002", utc(2026, 3, 2, 21, 0), replace(prov, source_id="0002"))
    store = FilingStore([original, amended])
    before = store.for_ticker("AAPL", utc(2026, 2, 15))
    assert [f.form for f in before] == ["10-K"]
    after = store.for_ticker("AAPL", utc(2026, 3, 3))
    assert {f.form for f in after} == {"10-K", "10-K/A"} and amended.is_amendment


# --- macro revisions ----------------------------------------------------------------------------

def test_macro_revision_is_invisible_until_released():
    payload = {"observations": [
        {"date": "2026-08-01", "realtime_start": "2026-09-05", "value": "142.0"},
        {"date": "2026-08-01", "realtime_start": "2026-10-03", "value": "120.0"},  # revision
        {"date": "2026-09-01", "realtime_start": "2026-10-03", "value": "."},  # missing -> skipped
    ]}
    store = MacroStore(parse_alfred_observations(payload, series_id="PAYEMS"))
    assert len(store) == 2
    sep = store.latest_value("PAYEMS", et_datetime(date(2026, 9, 20), "12:00"))
    assert sep is not None and sep.value == 142.0
    # same day as revision but before 08:30 ET release
    early = store.latest_value("PAYEMS", et_datetime(date(2026, 10, 3), "08:29"))
    assert early is not None and early.value == 142.0
    late = store.latest_value("PAYEMS", et_datetime(date(2026, 10, 3), "08:30"))
    assert late is not None and late.value == 120.0


def test_macro_observation_requires_aware_times():
    with pytest.raises(NaiveTimestampError):
        MacroObservation("X", datetime(2026, 1, 1), 1.0, utc(2026, 1, 2), Provenance("s", "i", "h"))


# --- cached features / models / training data ---------------------------------------------------

def test_model_trained_after_decision_cannot_score_it():
    with pytest.raises(LeakageViolation):
        assert_model_cutoff(utc(2026, 10, 9), utc(2026, 10, 8), model_id="m")
    assert_model_cutoff(utc(2026, 10, 1), utc(2026, 10, 8), model_id="m")
    assert_model_cutoff(None, utc(2026, 10, 8), model_id="frozen")


def test_text_state_ignores_future_articles_and_rejects_late_model(world):
    from icaif.nlp.event_impact import load_event_priors
    from icaif.nlp.feature_store import TextStateBuilder
    from icaif.nlp.relevance import LexicalEntityRelevance

    arts = world.articles[:80]
    as_of = arts[40].available_at
    future = make_article("future", "(AAPL) Apple raises guidance after strong results", as_of + timedelta(minutes=5))
    priors = load_event_priors()
    a = TextStateBuilder(arts, LexicalEntityRelevance(), priors)(as_of)
    b = TextStateBuilder([*arts, future], LexicalEntityRelevance(), priors)(as_of)
    assert np.array_equal(np.nan_to_num(a.score, nan=-9), np.nan_to_num(b.score, nan=-9))
    late = TextStateBuilder(arts, LexicalEntityRelevance(), priors, model_trained_through=as_of + timedelta(days=1))
    with pytest.raises(LeakageViolation):
        late(as_of)


def test_recency_rejects_future_items():
    with pytest.raises(LeakageViolation):
        age_hours(utc(2026, 10, 8, 14), utc(2026, 10, 8, 13))


def test_training_labels_must_end_before_boundary():
    boundary = utc(2026, 6, 30)
    with pytest.raises(LeakageViolation):
        assert_labels_before([utc(2026, 6, 29), utc(2026, 7, 1)], boundary, context="t")
    keep = purge([utc(2026, 6, 28), utc(2026, 6, 29)], [utc(2026, 6, 29), utc(2026, 7, 1)], boundary)
    assert keep == [0]


def test_temporal_split_requires_order_and_embargo():
    d = date
    ok = TemporalSplit(Segment("train", d(2025, 1, 1), d(2025, 12, 31)), Segment("dev", d(2026, 1, 5), d(2026, 3, 31)),
                       Segment("val", d(2026, 4, 3), d(2026, 6, 30)), Segment("test", d(2026, 7, 3), d(2026, 9, 30)))
    assert len(ok.segments()) == 3
    with pytest.raises(PermissionError):
        ok.unlock_final_test("yes")
    with pytest.raises(LeakageViolation):
        TemporalSplit(Segment("train", d(2025, 1, 1), d(2026, 1, 5)), Segment("dev", d(2026, 1, 5), d(2026, 3, 31)),
                      Segment("val", d(2026, 4, 3), d(2026, 6, 30)), Segment("test", d(2026, 7, 3), d(2026, 9, 30)))


# --- timestamps / timezones ---------------------------------------------------------------------

def test_naive_timestamps_rejected():
    with pytest.raises(NaiveTimestampError):
        parse_timestamp("2026-10-08T09:30:00")
    assert parse_timestamp("2026-10-08T13:30:00Z") == utc(2026, 10, 8, 13, 30)


def test_dst_transition_handled():
    # US DST ends 2026-11-01: 09:30 ET is 13:30Z before and 14:30Z after.
    assert et_datetime(date(2026, 10, 30), "09:30") == utc(2026, 10, 30, 13, 30)
    assert et_datetime(date(2026, 11, 2), "09:30") == utc(2026, 11, 2, 14, 30)


def test_stale_and_lagged_store_window():
    t0 = utc(2026, 10, 8, 12)
    arts = [make_article(str(i), f"n{i}", t0 + timedelta(hours=i)) for i in range(5)]
    store = PITStore(arts)
    win = store.window(t0 + timedelta(hours=3, minutes=30), t0 + timedelta(hours=2))
    assert [a.article_id for a in win] == ["2", "3"]
