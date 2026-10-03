from __future__ import annotations

import json
import math
import os
import stat
from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import full_weights
from icaif.competition.schedule import DeadlineError, generate_standard_schedule
from icaif.competition.submission import (
    DuplicateSubmissionError,
    SubmissionLedger,
    SubmissionValidationError,
    build_decision_payload,
    dumps_decision,
    prepare_round_submission,
    quantize_weights,
    validate_decision_payload,
    validate_weights,
    write_private_file,
)
from icaif.core.universe import SYMBOLS

SCHED = generate_standard_schedule("validation", [__import__("datetime").date(2026, 10, 8)])
ROW = SCHED.rounds[0]


def payload(weights=None, **kw):
    base = {"submission_type": "decision", "team_id": "team-1", "team_token": "tok-123", "phase": "validation",
            "round_id": ROW.id, "weights": weights if weights is not None else full_weights(0.0)}
    base.update(kw)
    return base


def test_valid_all_zero_and_full_weights():
    validate_decision_payload(payload())
    w = full_weights(0.0)
    for s in SYMBOLS[:4]:
        w[s] = 0.25
    validate_decision_payload(payload(w))


@pytest.mark.parametrize("mutate,msg", [
    (lambda w: w.pop("AAPL"), "exactly the 30"),
    (lambda w: w.update(ZZZZ=0.0), "exactly the 30"),
    (lambda w: w.update(AAPL=0.3000001), "between 0 and 0.30"),
    (lambda w: w.update(AAPL=-0.01), "between 0 and 0.30"),
    (lambda w: w.update(AAPL=math.nan), "finite"),
    (lambda w: w.update(AAPL=math.inf), "finite"),
    (lambda w: w.update(AAPL="0.1"), "JSON number"),
    (lambda w: w.update(AAPL=True), "JSON number"),
])
def test_invalid_weights(mutate, msg):
    w = full_weights(0.0)
    mutate(w)
    with pytest.raises(SubmissionValidationError, match=msg):
        validate_weights(w)


def test_sum_above_one_rejected_with_backend_tolerance():
    w = full_weights(0.0)
    for s in SYMBOLS[:4]:
        w[s] = Decimal("0.25")
    w[SYMBOLS[4]] = Decimal("1e-10")
    validate_weights(w)  # exactly 1 + 1e-10 tolerated
    w[SYMBOLS[4]] = Decimal("2e-10")
    with pytest.raises(SubmissionValidationError, match="exceeds 1"):
        validate_weights(w)


def test_round_and_phase_checks():
    with pytest.raises(SubmissionValidationError):
        validate_decision_payload(payload(round_id="validation-2026-10-08-r8"))
    with pytest.raises(SubmissionValidationError):
        validate_decision_payload(payload(phase="official"))
    with pytest.raises(SubmissionValidationError):
        validate_decision_payload(payload(extra=1))
    with pytest.raises(SubmissionValidationError, match="placeholders"):
        validate_decision_payload(payload(team_token="REPLACE_WITH_TEAM_TOKEN_FROM_REGISTRATION"))


def test_upload_window_checked_against_schedule():
    validate_decision_payload(payload(), schedule=SCHED, submitted_at=ROW.deadline - timedelta(seconds=1))
    with pytest.raises(SubmissionValidationError, match="window"):
        validate_decision_payload(payload(), schedule=SCHED, submitted_at=ROW.deadline)  # deadline exclusive
    validate_decision_payload(payload(), schedule=SCHED, submitted_at=ROW.opens_at)  # opening inclusive


def test_quantization_rounds_down_and_never_breaks_caps():
    w = {s: 1.0 / 30 for s in SYMBOLS}
    q = quantize_weights(w)
    assert sum(q.values()) <= 1 and all(v <= Decimal("0.3") for v in q.values())
    w2 = full_weights(0.0)
    w2["AAPL"] = 0.30000000000000004  # float noise above the cap
    assert quantize_weights(w2)["AAPL"] == Decimal("0.3")
    w3 = full_weights(0.0)
    w3["AAPL"] = -1e-12  # optimiser noise is clamped
    assert quantize_weights(w3)["AAPL"] == 0
    w4 = full_weights(0.0)
    w4["AAPL"] = -0.01
    with pytest.raises(SubmissionValidationError):
        quantize_weights(w4)


def test_json_contract_exact_and_parseable():
    p = build_decision_payload(team_id="t", team_token="k", phase="validation", round_id=ROW.id,
                               weights={**full_weights(0.0), "AAPL": 0.123456789})
    text = dumps_decision(p)
    parsed = json.loads(text, parse_float=Decimal)
    assert list(parsed) == ["submission_type", "team_id", "team_token", "phase", "round_id", "weights"]
    assert parsed["weights"]["AAPL"] == Decimal("0.12345678")
    assert set(parsed["weights"]) == set(SYMBOLS)
    assert "NaN" not in text and "e-" not in text


def test_private_file_mode_and_no_overwrite(tmp_path):
    path = write_private_file(tmp_path / "x" / "decision.json", "{}")
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    with pytest.raises(FileExistsError):
        write_private_file(path, "{}")


def test_ledger_idempotency_survives_restart(tmp_path):
    ledger = SubmissionLedger(tmp_path / "ledger.jsonl")
    ledger.claim("validation", ROW.id, full_weights(0.0))
    with pytest.raises(DuplicateSubmissionError):
        ledger.claim("validation", ROW.id, full_weights(0.01))  # different weights: still refused
    ledger.mark("validation", ROW.id, "submitted")
    reloaded = SubmissionLedger(tmp_path / "ledger.jsonl")
    assert reloaded.get("validation", ROW.id).state == "submitted"
    with pytest.raises(DuplicateSubmissionError):
        reloaded.claim("validation", ROW.id, full_weights(0.0))
    reloaded.record_skip("validation", SCHED.rounds[1].id, "agent_hold")
    with pytest.raises(DuplicateSubmissionError):
        reloaded.claim("validation", SCHED.rounds[1].id, full_weights(0.0))


def test_prepare_round_submission_deadline_guard(tmp_path):
    ledger = SubmissionLedger(tmp_path / "l.jsonl")
    w = full_weights(0.0)
    with pytest.raises(DeadlineError):
        prepare_round_submission(row=ROW, weights=w, team_id="t", team_token="k", now=ROW.deadline - timedelta(seconds=30),
                                 ledger=ledger, safety_margin_seconds=60)
    with pytest.raises(DeadlineError):
        prepare_round_submission(row=ROW, weights=w, team_id="t", team_token="k", now=ROW.opens_at - timedelta(seconds=1),
                                 ledger=ledger, safety_margin_seconds=60)
    assert ledger.get("validation", ROW.id) is None  # a refused attempt does not consume the ledger slot
    p, text = prepare_round_submission(row=ROW, weights=w, team_id="t", team_token="k",
                                       now=ROW.deadline - timedelta(minutes=10), ledger=ledger, safety_margin_seconds=60)
    assert p["round_id"] == ROW.id and json.loads(text)["phase"] == "validation"
    with pytest.raises(DuplicateSubmissionError):
        prepare_round_submission(row=ROW, weights=w, team_id="t", team_token="k",
                                 now=ROW.deadline - timedelta(minutes=9), ledger=ledger, safety_margin_seconds=60)
