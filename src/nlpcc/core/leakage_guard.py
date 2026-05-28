"""Decision-time leakage checks for canonical contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Iterable

from nlpcc.core.data_contracts import DailyDecisionInput, PriceBar, PriceVisibility, RawNewsItem


OFFICIAL_NEWS_CUTOFF = time(15, 0)


class LeakageViolation(ValueError):
    """Raised when decision-time inputs expose prohibited future information."""


@dataclass(frozen=True)
class LeakageIssue:
    code: str
    message: str
    fund_id: str | None = None
    date_int: int | None = None


def _date_int_from_datetime(value: datetime) -> int:
    return int(value.strftime("%Y%m%d"))


def find_price_visibility_issues(bars: Iterable[PriceBar], decision_date: int) -> list[LeakageIssue]:
    issues: list[LeakageIssue] = []
    for bar in bars:
        if bar.date_int > decision_date:
            issues.append(
                LeakageIssue(
                    code="future_price_bar",
                    message="Price bar date is after the decision date.",
                    fund_id=bar.fund_id,
                    date_int=bar.date_int,
                )
            )
        if bar.date_int == decision_date:
            unsafe = bar.unsafe_current_fields
            if unsafe:
                issues.append(
                    LeakageIssue(
                        code="current_day_price_leakage",
                        message=f"Current decision day exposes forbidden fields: {sorted(unsafe)}.",
                        fund_id=bar.fund_id,
                        date_int=bar.date_int,
                    )
                )
            if bar.visibility != PriceVisibility.CURRENT_OPEN_ONLY:
                issues.append(
                    LeakageIssue(
                        code="current_day_visibility_mismatch",
                        message="Current decision day price bar must be marked current_open_only.",
                        fund_id=bar.fund_id,
                        date_int=bar.date_int,
                    )
                )
        if bar.date_int < decision_date and bar.visibility == PriceVisibility.CURRENT_OPEN_ONLY:
            issues.append(
                LeakageIssue(
                    code="past_day_visibility_mismatch",
                    message="Past price bars should be marked historical_full.",
                    fund_id=bar.fund_id,
                    date_int=bar.date_int,
                )
            )
    return issues


def find_news_cutoff_issues(
    news_items: Iterable[RawNewsItem],
    decision_date: int,
    cutoff: time = OFFICIAL_NEWS_CUTOFF,
) -> list[LeakageIssue]:
    issues: list[LeakageIssue] = []
    for item in news_items:
        if item.publish_time is None:
            issues.append(
                LeakageIssue(
                    code="missing_news_publish_time",
                    message="News item is missing publish_time, so cutoff safety cannot be verified.",
                )
            )
            continue
        publish_date = _date_int_from_datetime(item.publish_time)
        if publish_date > decision_date:
            issues.append(
                LeakageIssue(
                    code="future_news",
                    message="News publish date is after the decision date.",
                    date_int=publish_date,
                )
            )
        if publish_date == decision_date and item.publish_time.time() >= cutoff:
            issues.append(
                LeakageIssue(
                    code="same_day_news_after_cutoff",
                    message=f"Same-day news must be before {cutoff.strftime('%H:%M')}.",
                    date_int=publish_date,
                )
            )
    return issues


def find_decision_input_issues(decision_input: DailyDecisionInput) -> list[LeakageIssue]:
    issues = find_price_visibility_issues(decision_input.prices.all_bars(), decision_input.decision_date)
    issues.extend(find_news_cutoff_issues(decision_input.news, decision_input.decision_date))
    return issues


def assert_no_leakage(decision_input: DailyDecisionInput) -> None:
    issues = find_decision_input_issues(decision_input)
    if issues:
        joined = "; ".join(f"{issue.code}: {issue.message}" for issue in issues)
        raise LeakageViolation(joined)
