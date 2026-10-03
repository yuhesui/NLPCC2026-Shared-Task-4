from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from icaif.competition.evaluation import Period, compute_official_metrics, overall_rank_scores
from icaif.competition.portfolio_state import (
    PortfolioState,
    PortfolioStateIncomplete,
    parse_portfolio_payload,
)
from icaif.competition.schedule import (
    Round,
    Schedule,
    ScheduleError,
    generate_standard_schedule,
    parse_round_id,
)
from icaif.core.time import et_datetime
from icaif.core.universe import SYMBOLS


def test_standard_schedule_shape_and_windows():
    s = generate_standard_schedule("official", [date(2026, 10, 12), date(2026, 10, 13)])
    rounds = s.phase_rounds("official")
    assert len(rounds) == 14 and [r.number for r in rounds[:7]] == list(range(1, 8))
    r1_day2 = s.get("official-2026-10-13-r1")
    assert r1_day2.opens_at == et_datetime(date(2026, 10, 12), "15:40")  # previous day last execution + 10 min
    r2 = s.get("official-2026-10-12-r2")
    assert r2.opens_at == et_datetime(date(2026, 10, 12), "09:40") and r2.deadline == et_datetime(date(2026, 10, 12), "10:25")
    assert s.get("official-2026-10-12-r1").opens_at == et_datetime(date(2026, 10, 9), "15:40")  # Friday before


def test_active_round_boundaries():
    s = generate_standard_schedule("validation", [date(2026, 10, 8)])
    r3 = s.get("validation-2026-10-08-r3")
    assert s.active_round(r3.opens_at, "validation") == r3
    assert s.active_round(r3.deadline, "validation") is None  # deadline exclusive; gap is "late"
    assert s.active_round(r3.deadline - timedelta(microseconds=1), "validation") == r3
    assert s.next_round(r3.deadline, "validation").number == 4


def test_cancelled_rounds_excluded():
    s = generate_standard_schedule("validation", [date(2026, 10, 8)])
    rows = [r.as_dict() for r in s.rounds]
    rows[6]["status"] = "CANCELLED"
    s2 = Schedule.from_official({"rounds": rows})
    assert len(s2.phase_rounds("validation")) == 6
    assert s2.active_round(s2.rounds[6].opens_at, "validation") is None


def test_round_id_validation():
    assert parse_round_id("official-2026-10-30-r7") == ("official", date(2026, 10, 30), 7)
    with pytest.raises(ScheduleError):
        parse_round_id("official-2026-10-30-r0")
    row = generate_standard_schedule("validation", [date(2026, 10, 8)]).rounds[0]
    with pytest.raises(ScheduleError):
        Round(**{**row.__dict__, "id": "official-2026-10-08-r1"})
    with pytest.raises(ScheduleError):
        Schedule.from_official({"rounds": [row.as_dict(), row.as_dict()]})


def test_official_example_metrics():
    # starter-kit/examples/evaluation.json -> evaluation_expected.json
    periods = [Period(1_000_000, 900_000, 300_000), Period(900_000, 990_000, 450_000)]
    m = compute_official_metrics(periods, [1_000_000, 900_000, 800_000, 990_000])
    assert m.cumulative_return == pytest.approx(-0.01)
    assert m.sharpe_ratio == 0.0  # mean return exactly 0
    assert m.maximum_drawdown == pytest.approx(0.2)
    assert m.turnover == pytest.approx(0.4)


def test_metrics_reject_discontinuous_periods():
    with pytest.raises(ValueError):
        compute_official_metrics([Period(1_000_000, 1_010_000, 0), Period(1_000_000, 1_000_000, 0)], [1_000_000, 1_010_000, 1_000_000])


def test_sharpe_uses_42_and_sample_std():
    r = np.array([0.01, -0.005, 0.002, 0.004])
    navs = 1_000_000 * np.cumprod(np.concatenate([[1.0], 1 + r]))
    periods = [Period(navs[i], navs[i + 1], 0.0) for i in range(4)]
    m = compute_official_metrics(periods, list(navs))
    assert m.sharpe_ratio == pytest.approx(42 * r.mean() / r.std(ddof=1), rel=1e-9)


def test_rank_scores_ties_and_tiebreaks():
    pop = {
        "a": {"cumulative_return": 0.05, "sharpe_ratio": 2.0, "maximum_drawdown": 0.02, "turnover": 0.1},
        "b": {"cumulative_return": 0.05, "sharpe_ratio": 1.0, "maximum_drawdown": 0.01, "turnover": 0.2},
        "c": {"cumulative_return": 0.01, "sharpe_ratio": 0.5, "maximum_drawdown": 0.05, "turnover": 0.05},
    }
    r = overall_rank_scores(pop)
    assert r["a"]["rank_cumulative_return"] == r["b"]["rank_cumulative_return"] == 1.5
    assert r["a"]["overall_rank_score"] == pytest.approx((1.5 + 1 + 2 + 2) / 4)
    assert r["b"]["overall_rank_score"] == pytest.approx((1.5 + 2 + 1 + 3) / 4)
    assert r["a"]["position"] == 1.0


def test_portfolio_payload_shapes_and_incomplete_state():
    st = parse_portfolio_payload({"cash": 1000.0, "positions": {"AAPL": {"shares": 2.5, "price": 200.0}}})
    assert st.shares[SYMBOLS.index("AAPL")] == 2.5 and st.reference_prices is not None
    st2 = parse_portfolio_payload({"portfolio": {"cash": "5", "holdings": [{"symbol": "MSFT", "quantity": 1}]}})
    assert st2.cash == 5.0
    for bad in ({}, {"cash": 1}, {"cash": 1, "positions": {"ZZZ": 1}}, {"cash": float("nan"), "positions": {}},
                {"cash": 1, "positions": {"AAPL": {"shares": None}}}):
        with pytest.raises(PortfolioStateIncomplete):
            parse_portfolio_payload(bad)
    with pytest.raises(PortfolioStateIncomplete):
        PortfolioState(cash=0.0, shares=(-1.0,) + (0.0,) * 29)


def test_drifted_weights():
    st = PortfolioState(cash=500.0, shares=(1.0,) + (0.0,) * 29)
    px = np.full(30, 10.0)
    px[0] = 500.0
    w = st.weights(px)
    assert w[0] == pytest.approx(0.5) and st.nav(px) == pytest.approx(1000.0)
