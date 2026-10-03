"""Cross-checks against the official starter kit (skipped when third_party kit is absent)."""

from __future__ import annotations

import json
import math
from datetime import timedelta
from decimal import Decimal

import numpy as np
import pytest

from conftest import full_weights
from icaif.competition.evaluation import Period, compute_official_metrics
from icaif.competition.official_adapter import load_official_kit
from icaif.competition.schedule import Schedule, generate_standard_schedule
from icaif.competition.submission import SubmissionValidationError, dumps_decision, validate_decision_payload
from icaif.core import constants
from icaif.core.universe import SECTORS, SYMBOLS

pytestmark = pytest.mark.official_kit


@pytest.fixture(scope="module")
def kit():
    return load_official_kit()


def test_universe_and_constants_match(kit):
    assert kit.symbols() == list(SYMBOLS)
    uni = json.loads((kit.root / "universe.json").read_text())
    assert {k: tuple(v) for k, v in uni["sectors"].items()} == dict(SECTORS)
    comp = kit.competition()
    assert tuple(comp["round_deadlines_et"]) == constants.ROUND_DEADLINES_ET
    assert tuple(comp["round_execution_times_et"]) == constants.ROUND_EXECUTION_TIMES_ET
    assert comp["regular_close_et"] == constants.REGULAR_CLOSE_ET
    assert comp["upload_delay_minutes"] == constants.UPLOAD_DELAY_MINUTES
    assert {k: tuple(v) for k, v in comp["phase_dates"].items()} == constants.PHASE_DATES
    assert kit.evaluation.CALCULATION_VERSION == constants.METRICS_CALCULATION_VERSION


def test_generated_schedule_equals_official_bundle(kit):
    official = Schedule.from_official(kit.schedule())
    for phase, n in (("validation", 14), ("official", 105)):
        rounds = official.phase_rounds(phase)
        assert len(rounds) == n
        generated = generate_standard_schedule(phase, official.trading_days(phase)).phase_rounds(phase)
        assert [r.as_dict() for r in generated] == [r.as_dict() for r in rounds]


def _cases():
    zero = full_weights(0.0)
    four = {**zero, **dict.fromkeys(SYMBOLS[:4], 0.25)}
    over_cap = {**zero, "AAPL": 0.31}
    over_sum = {**zero, **dict.fromkeys(SYMBOLS[:4], 0.3)}
    missing = {k: v for k, v in zero.items() if k != "NEE"}
    return [("zero", zero, True), ("four", four, True), ("over_cap", over_cap, False), ("over_sum", over_sum, False),
            ("missing", missing, False), ("string", {**zero, "AAPL": "0.1"}, False)]


@pytest.mark.parametrize("name,weights,valid", _cases())
def test_validators_agree(kit, tmp_path, name, weights, valid):
    payload = {"submission_type": "decision", "team_id": "team-x", "team_token": "token-x", "phase": "official",
               "round_id": "official-2026-10-12-r1", "weights": weights}
    ours = True
    try:
        validate_decision_payload(payload)
    except SubmissionValidationError:
        ours = False
    path = tmp_path / "decision.json"
    path.write_text(dumps_decision(payload) if all(isinstance(v, float | int) for v in weights.values())
                    else json.dumps(payload), encoding="utf-8")
    theirs = True
    try:
        kit.validate_decision_file(path)
    except ValueError:
        theirs = False
    assert ours == theirs == valid


def test_official_window_semantics(kit, tmp_path):
    sched = Schedule.from_official(kit.schedule())
    row = sched.get("official-2026-10-12-r1")
    payload = {"submission_type": "decision", "team_id": "team-x", "team_token": "token-x", "phase": "official",
               "round_id": row.id, "weights": full_weights(0.0)}
    path = tmp_path / "decision.json"
    path.write_text(dumps_decision(payload))
    kit.validate_decision_file(path, submitted_at=(row.deadline - timedelta(seconds=1)).isoformat())
    with pytest.raises(ValueError):
        kit.validate_decision_file(path, submitted_at=row.deadline.isoformat())


def test_metrics_parity_with_official_calculator(kit):
    rng = np.random.default_rng(3)
    nav = 1_000_000.0
    periods, points = [], [nav]
    for k in range(40):
        end = nav * (1 + rng.normal(0, 0.004))
        periods.append(Period(nav, end, abs(rng.normal(0, 0.1)) * nav))
        if k % 7 == 6:
            points.append(end * (1 + rng.normal(0, 0.002)))  # an intermediate daily close inside a period
        points.append(end)
        nav = end
    ours = compute_official_metrics(periods, points)
    theirs = kit.calculate_metrics(
        [{"nav_before": repr(p.nav_before), "nav_after_period": repr(p.nav_after_period),
          "traded_notional": repr(p.traded_notional)} for p in periods], [repr(v) for v in points])
    for key in ("cumulative_return", "sharpe_ratio", "maximum_drawdown", "turnover"):
        assert math.isclose(getattr(ours, key), float(theirs[key]), rel_tol=1e-12, abs_tol=1e-15), key
    assert isinstance(theirs["sharpe_ratio"], Decimal)
