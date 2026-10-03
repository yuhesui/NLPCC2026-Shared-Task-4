"""decision.json construction, independent validation and submission idempotency.

Validation mirrors the official ``kit/contracts.py`` rules with exact Decimal
arithmetic. When the official kit is available the adapter *additionally*
runs the kit's own ``validate_payload`` (see ``official_adapter.py``); the two
must agree (tested in ``tests/competition``).

Weights are serialised as exact decimal strings quantised **down** to
``WEIGHT_DECIMALS`` places, so rounding can never push a weight above 0.30 or
the total above 1.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_DOWN, Context, Decimal, localcontext
from pathlib import Path
from typing import Any

from icaif.competition.schedule import Round, Schedule, assert_submission_window
from icaif.core.constants import MAX_SUBMISSION_BYTES, MAX_WEIGHT, ROUND_ID_PATTERN, WEIGHT_SUM_TOLERANCE
from icaif.core.schemas import content_hash
from icaif.core.time import ensure_aware, utc_now
from icaif.core.universe import SYMBOLS

WEIGHT_DECIMALS = 8
_QUANT = Decimal(1).scaleb(-WEIGHT_DECIMALS)
_CAP = Decimal(str(MAX_WEIGHT))
_PLACEHOLDER = re.compile(r"\b(?:DEMO|REPLACE)(?:[_ -]|$)", re.IGNORECASE)
DECISION_FIELDS = frozenset({"submission_type", "team_id", "team_token", "phase", "round_id", "weights"})


class SubmissionValidationError(ValueError):
    """Message contains field labels only, never credential values."""


def quantize_weights(weights: Mapping[str, float]) -> dict[str, Decimal]:
    """Exact, round-down decimal weights in official symbol order."""

    if set(weights) != set(SYMBOLS):
        missing = sorted(set(SYMBOLS) - set(weights))
        unknown = sorted(set(weights) - set(SYMBOLS))
        raise SubmissionValidationError(f"weights must cover exactly the 30 symbols (missing={missing}, unknown={unknown})")
    out: dict[str, Decimal] = {}
    for symbol in SYMBOLS:
        value = weights[symbol]
        if isinstance(value, bool) or not isinstance(value, int | float | Decimal):
            raise SubmissionValidationError(f"weight for {symbol} must be numeric")
        number = Decimal(str(value)) if not isinstance(value, Decimal) else value
        if not number.is_finite():
            raise SubmissionValidationError(f"weight for {symbol} must be finite")
        if number < 0:
            # Tiny negative float noise from optimisers is clamped; anything
            # material is a bug upstream and must not be hidden.
            if number < Decimal("-1e-9"):
                raise SubmissionValidationError(f"weight for {symbol} is negative")
            number = Decimal(0)
        q = number.quantize(_QUANT, rounding=ROUND_DOWN)
        out[symbol] = min(q, _CAP)
    return out


def validate_weights(weights: Mapping[str, Any]) -> None:
    """Official weight rules: exact symbol set, JSON numbers, 0..0.30, sum <= 1 (+1e-10)."""

    if not isinstance(weights, Mapping) or set(weights) != set(SYMBOLS):
        raise SubmissionValidationError("weights must contain exactly the 30 official symbols, including zero targets")
    with localcontext(Context(prec=40)):
        total = Decimal(0)
        for symbol in SYMBOLS:
            value = weights[symbol]
            if isinstance(value, bool) or not isinstance(value, int | float | Decimal):
                raise SubmissionValidationError("every weight must be a JSON number, not a string or boolean")
            if isinstance(value, float) and not math.isfinite(value):
                raise SubmissionValidationError("every weight must be finite")
            number = value if isinstance(value, Decimal) else Decimal(str(value))
            if not number.is_finite() or not Decimal(0) <= number <= _CAP:
                raise SubmissionValidationError("every weight must be finite and between 0 and 0.30")
            total += number
        if total > Decimal(1) + WEIGHT_SUM_TOLERANCE:
            raise SubmissionValidationError("total stock weight exceeds 1")


def _check_text(value: Any, label: str, maximum: int = 200) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise SubmissionValidationError(f"{label} must be non-empty text of at most {maximum} characters")


def validate_decision_payload(
    payload: Mapping[str, Any],
    *,
    schedule: Schedule | None = None,
    submitted_at: datetime | None = None,
    allow_placeholders: bool = False,
) -> None:
    if not isinstance(payload, Mapping) or payload.get("submission_type") != "decision":
        raise SubmissionValidationError("submission_type must be 'decision'")
    if set(payload) != DECISION_FIELDS:
        raise SubmissionValidationError("decision has missing or unknown fields")
    _check_text(payload["team_id"], "team_id")
    _check_text(payload["team_token"], "team_token")
    if not allow_placeholders and any(_PLACEHOLDER.search(str(payload[k])) for k in ("team_id", "team_token")):
        raise SubmissionValidationError("replace DEMO/REPLACE placeholders before a live submission")
    if payload["phase"] not in ("validation", "official"):
        raise SubmissionValidationError("phase must be validation or official")
    round_id = payload["round_id"]
    if not isinstance(round_id, str) or not re.match(ROUND_ID_PATTERN, round_id):
        raise SubmissionValidationError("round_id has the wrong format")
    if not round_id.startswith(payload["phase"] + "-"):
        raise SubmissionValidationError("round_id does not belong to phase")
    validate_weights(payload["weights"])
    if schedule is not None:
        row = schedule.get(round_id)
        if row.phase != payload["phase"] or row.cancelled:
            raise SubmissionValidationError("phase/round_id must name a non-cancelled round in the schedule")
        if submitted_at is not None and not row.window_contains(ensure_aware(submitted_at)):
            raise SubmissionValidationError("upload time must be inside the round window, strictly before its deadline")


def build_decision_payload(
    *, team_id: str, team_token: str, phase: str, round_id: str, weights: Mapping[str, float]
) -> dict[str, Any]:
    payload = {
        "submission_type": "decision",
        "team_id": team_id,
        "team_token": team_token,
        "phase": phase,
        "round_id": round_id,
        "weights": quantize_weights(weights),
    }
    validate_decision_payload(payload, allow_placeholders=True)
    return payload


def dumps_decision(payload: Mapping[str, Any]) -> str:
    """Encode exactly (Decimal -> JSON number text), mirroring kit ``dumps_json``."""

    def encode(value: Any) -> str:
        if isinstance(value, Decimal):
            if not value.is_finite():
                raise SubmissionValidationError("JSON numbers must be finite")
            text = format(value.normalize(), "f")
            return "0" if text in ("-0", "0") else text
        if isinstance(value, Mapping):
            return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + encode(v) for k, v in value.items()) + "}"
        if isinstance(value, list | tuple):
            return "[" + ",".join(encode(v) for v in value) + "]"
        return json.dumps(value, ensure_ascii=False, allow_nan=False)

    text = encode(payload)
    if len(text.encode("utf-8")) > MAX_SUBMISSION_BYTES:
        raise SubmissionValidationError("decision exceeds the 120000-byte limit")
    return text


def write_private_file(path: Path, text: str) -> Path:
    """Write with mode 0600; never overwrite (mirrors the kit agent's behaviour)."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)
    return path


# ----------------------------------------------------------------------------
# Idempotency: one intended submission per (phase, round)
# ----------------------------------------------------------------------------


class DuplicateSubmissionError(RuntimeError):
    pass


@dataclass(frozen=True)
class LedgerEntry:
    phase: str
    round_id: str
    weights_hash: str
    state: str  # "intended" -> "submitted" | "skipped" | "failed_before_upload"
    recorded_at: str
    note: str = ""


class SubmissionLedger:
    """Local append-only record of submission *intents*.

    The platform consumes a round on the first attributable in-window upload,
    even if invalid, so the safe policy is: record the intent atomically
    *before* uploading; refuse any second intent for the same round, whatever
    its weights. Recovery of an ambiguous upload is delegated to the official
    client's checkpoint (``resolve``/``fetch``), never to a re-upload.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._entries: dict[str, LedgerEntry] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    self._entries[self._key(row["phase"], row["round_id"])] = LedgerEntry(**row)

    @staticmethod
    def _key(phase: str, round_id: str) -> str:
        return f"{phase}:{round_id}"

    def get(self, phase: str, round_id: str) -> LedgerEntry | None:
        return self._entries.get(self._key(phase, round_id))

    def _append(self, entry: LedgerEntry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry.__dict__, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self._entries[self._key(entry.phase, entry.round_id)] = entry

    def claim(self, phase: str, round_id: str, weights: Mapping[str, Any], *, now: datetime | None = None) -> LedgerEntry:
        existing = self.get(phase, round_id)
        if existing is not None:
            raise DuplicateSubmissionError(
                f"round {round_id} already has a recorded intent (state={existing.state}); refusing a second upload"
            )
        entry = LedgerEntry(
            phase=phase,
            round_id=round_id,
            weights_hash=content_hash({k: str(v) for k, v in weights.items()}),
            state="intended",
            recorded_at=(now or utc_now()).isoformat(),
        )
        self._append(entry)
        return entry

    def mark(self, phase: str, round_id: str, state: str, note: str = "") -> LedgerEntry:
        existing = self.get(phase, round_id)
        if existing is None:
            raise KeyError(f"no intent recorded for {round_id}")
        entry = LedgerEntry(existing.phase, existing.round_id, existing.weights_hash, state, utc_now().isoformat(), note)
        self._append(entry)
        return entry

    def record_skip(self, phase: str, round_id: str, reason: str) -> LedgerEntry:
        """Record an explicit HOLD (no upload) so restarts do not reconsider it."""

        if self.get(phase, round_id) is not None:
            raise DuplicateSubmissionError(f"round {round_id} already decided")
        entry = LedgerEntry(phase, round_id, "", "skipped", utc_now().isoformat(), reason)
        self._append(entry)
        return entry


def prepare_round_submission(
    *,
    row: Round,
    weights: Mapping[str, float],
    team_id: str,
    team_token: str,
    now: datetime,
    ledger: SubmissionLedger,
    safety_margin_seconds: float,
) -> tuple[dict[str, Any], str]:
    """Deadline guard -> validation -> ledger claim -> exact JSON text."""

    from datetime import timedelta

    assert_submission_window(row, now, safety_margin=timedelta(seconds=safety_margin_seconds))
    payload = build_decision_payload(
        team_id=team_id, team_token=team_token, phase=row.phase, round_id=row.id, weights=weights
    )
    validate_decision_payload(payload)
    ledger.claim(row.phase, row.id, payload["weights"], now=now)
    return payload, dumps_decision(payload)
