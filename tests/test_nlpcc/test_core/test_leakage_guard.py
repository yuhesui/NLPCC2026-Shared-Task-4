from datetime import datetime

import pytest

from nlpcc.core.data_contracts import (
    DailyDecisionInput,
    DecisionTrace,
    PortfolioState,
    PriceBar,
    PricePanel,
    PriceVisibility,
    RawNewsItem,
)
from nlpcc.core.leakage_guard import (
    LeakageViolation,
    assert_no_leakage,
    find_decision_input_issues,
)


def _decision_input(*, current_bar: PriceBar, news: tuple[RawNewsItem, ...] = ()) -> DailyDecisionInput:
    past_bar = PriceBar(
        fund_id="FUND_A",
        date_int=20250102,
        open=10.0,
        close=10.5,
        high=10.7,
        low=9.9,
        volume=1000.0,
        visibility=PriceVisibility.HISTORICAL_FULL,
    )
    panel = PricePanel({"FUND_A": (past_bar, current_bar)})
    return DailyDecisionInput(
        decision_date=20250103,
        track="macro",
        fund_pool=("FUND_A",),
        news=news,
        prices=panel,
        portfolio=PortfolioState(cash=1000.0),
        trace=DecisionTrace(decision_id="test", decision_date=20250103),
    )


def test_allows_past_full_prices_current_open_only_and_pre_cutoff_news() -> None:
    current_bar = PriceBar(
        fund_id="FUND_A",
        date_int=20250103,
        open=10.6,
        visibility=PriceVisibility.CURRENT_OPEN_ONLY,
    )
    news = (
        RawNewsItem(
            source="official",
            title="Before cutoff",
            content=None,
            ranking=1,
            publish_time=datetime(2025, 1, 3, 14, 59),
        ),
    )

    assert_no_leakage(_decision_input(current_bar=current_bar, news=news))


def test_rejects_current_day_close_high_low_and_return_fields() -> None:
    current_bar = PriceBar(
        fund_id="FUND_A",
        date_int=20250103,
        open=10.6,
        close=10.8,
        high=10.9,
        low=10.5,
        return_=0.02,
        visibility=PriceVisibility.CURRENT_OPEN_ONLY,
    )
    decision_input = _decision_input(current_bar=current_bar)

    issues = find_decision_input_issues(decision_input)

    assert "current_day_price_leakage" in {issue.code for issue in issues}
    with pytest.raises(LeakageViolation):
        assert_no_leakage(decision_input)


def test_rejects_current_day_bar_without_open_only_visibility() -> None:
    current_bar = PriceBar(
        fund_id="FUND_A",
        date_int=20250103,
        open=10.6,
        visibility=PriceVisibility.HISTORICAL_FULL,
    )

    issues = find_decision_input_issues(_decision_input(current_bar=current_bar))

    assert "current_day_visibility_mismatch" in {issue.code for issue in issues}


def test_rejects_same_day_news_at_or_after_cutoff() -> None:
    current_bar = PriceBar(
        fund_id="FUND_A",
        date_int=20250103,
        open=10.6,
        visibility=PriceVisibility.CURRENT_OPEN_ONLY,
    )
    news = (
        RawNewsItem(
            source="official",
            title="At cutoff",
            content=None,
            ranking=1,
            publish_time=datetime(2025, 1, 3, 15, 0),
        ),
    )

    issues = find_decision_input_issues(_decision_input(current_bar=current_bar, news=news))

    assert "same_day_news_after_cutoff" in {issue.code for issue in issues}


def test_rejects_future_news() -> None:
    current_bar = PriceBar(
        fund_id="FUND_A",
        date_int=20250103,
        open=10.6,
        visibility=PriceVisibility.CURRENT_OPEN_ONLY,
    )
    news = (
        RawNewsItem(
            source="official",
            title="Tomorrow",
            content=None,
            ranking=1,
            publish_time=datetime(2025, 1, 4, 9, 0),
        ),
    )

    issues = find_decision_input_issues(_decision_input(current_bar=current_bar, news=news))

    assert "future_news" in {issue.code for issue in issues}
