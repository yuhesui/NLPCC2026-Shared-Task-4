"""Timezone-strict time helpers.

Every timestamp inside the package is a timezone-aware ``datetime``; naive
values are rejected rather than silently localised. Internally we compare in
UTC; Eastern Time is used only for schedule construction and display.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from icaif.core.constants import TIMEZONE

ET = ZoneInfo(TIMEZONE)


class NaiveTimestampError(ValueError):
    """Raised when a timestamp lacks timezone information."""


def ensure_aware(value: datetime, label: str = "timestamp") -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{label} must be a datetime, got {type(value).__name__}")
    if value.tzinfo is None or value.utcoffset() is None:
        raise NaiveTimestampError(f"{label} must be timezone-aware: {value!r}")
    return value.astimezone(UTC)


def parse_timestamp(value: str | datetime, label: str = "timestamp") -> datetime:
    """Parse an ISO-8601 string (``Z`` accepted) into an aware UTC datetime."""

    if isinstance(value, datetime):
        return ensure_aware(value, label)
    if not isinstance(value, str):
        raise TypeError(f"{label} must be an ISO-8601 string or datetime")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{label} is not ISO-8601: {value!r}") from error
    return ensure_aware(parsed, label)


def to_iso(value: datetime) -> str:
    return ensure_aware(value).isoformat()


def et_datetime(day: date, hhmm: str) -> datetime:
    """Eastern-time wall clock on ``day`` converted to aware UTC (DST-correct)."""

    hour, minute = (int(part) for part in hhmm.split(":"))
    return datetime.combine(day, time(hour, minute), tzinfo=ET).astimezone(UTC)


def et_date(value: datetime) -> date:
    return ensure_aware(value).astimezone(ET).date()


def minutes(n: float) -> timedelta:
    return timedelta(minutes=n)


def utc_now() -> datetime:
    return datetime.now(UTC)
