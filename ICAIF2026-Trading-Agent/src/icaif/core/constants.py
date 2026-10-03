"""Competition constants derived from the official ICAIF 2026 starter kit.

Source of truth: DeepIntoStreams/2026ICAIF_Trading_Agent_Competition, files
``starter-kit/competition.json``, ``universe.json``, ``docs/rules.md`` and
``docs/evaluation.md`` (inspected at commit ad237b07, 2026-09-21).
``tests/competition/test_official_kit_parity.py`` re-checks these values
against a local checkout of the kit whenever one is present.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Final

TIMEZONE: Final = "America/New_York"

INITIAL_NAV: Final = 1_000_000.0
MAX_WEIGHT: Final = 0.30
MAX_GROSS: Final = 1.0
# Backend tolerance on the weight sum (kit/contracts.py: total <= 1 + 1e-10).
WEIGHT_SUM_TOLERANCE: Final = Decimal("1e-10")
# 0.1% of total buy + sell notional per rebalance, initial allocation included.
FEE_RATE: Final = 0.001

ROUNDS_PER_DAY: Final = 7
ROUND_EXECUTION_TIMES_ET: Final = ("09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30")
ROUND_DEADLINES_ET: Final = ("09:10", "10:25", "11:25", "12:25", "13:25", "14:25", "15:25")
REGULAR_CLOSE_ET: Final = "16:00"
# A window opens 10 minutes after the preceding execution (R1: previous day's
# last active execution + 10 min, normally 15:40).
UPLOAD_DELAY_MINUTES: Final = 10

# Sharpe annualisation: sqrt(252 * 7) = sqrt(1764) = 42, fixed even when
# rounds are cancelled (docs/evaluation.md).
SHARPE_ANNUALISATION: Final = 42.0
METRICS_CALCULATION_VERSION: Final = "decision-period-sharpe1764-turnover-mean-shared-ties-decimal40-v2"

PHASES: Final = ("validation", "official")
ROUND_ID_PATTERN: Final = r"^(validation|official)-[0-9]{4}-[0-9]{2}-[0-9]{2}-r[1-7]$"
MAX_SUBMISSION_BYTES: Final = 120_000

PHASE_DATES: Final = {
    "validation": ("2026-10-08", "2026-10-09"),
    "official": ("2026-10-12", "2026-10-30"),
}
