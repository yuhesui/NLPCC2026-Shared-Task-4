from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from icaif.competition.official_adapter import kit_available
from icaif.competition.schedule import generate_standard_schedule
from icaif.core.schemas import Article, MarketBar, Provenance, content_hash
from icaif.core.universe import SYMBOLS
from icaif.data.market.synthetic import SyntheticConfig, generate_synthetic_world


@pytest.fixture(scope="session")
def world():
    return generate_synthetic_world(SyntheticConfig(days=30, seed=11))


@pytest.fixture(scope="session")
def eval_schedule(world):
    return generate_standard_schedule("validation", world.panel.trading_days()[20:23])


def pytest_collection_modifyitems(config, items):
    if kit_available():
        return
    skip = pytest.mark.skip(reason="official kit not fetched (scripts/setup/fetch_official_kit.sh)")
    for item in items:
        if "official_kit" in item.keywords:
            item.add_marker(skip)


def make_article(aid: str, title: str, published: datetime, *, delay_s: int = 60, body: str = "", source: str = "test") -> Article:
    return Article(article_id=aid, title=title, body=body or title, source=source, published_at=published,
                   available_at=published + timedelta(seconds=delay_s),
                   provenance=Provenance(source, aid, content_hash(title + body)), language="en")


def make_bar(symbol: str, start: datetime, minutes: int = 30, price: float = 100.0, delay_s: int = 60) -> MarketBar:
    end = start + timedelta(minutes=minutes)
    return MarketBar(symbol, start, end, price, price * 1.01, price * 0.99, price, 1000.0, end + timedelta(seconds=delay_s),
                     Provenance("test", f"{symbol}:{start.isoformat()}", "h"))


def full_weights(value: float = 0.0) -> dict[str, float]:
    return dict.fromkeys(SYMBOLS, value)


def utc(*args: int) -> datetime:
    return datetime(*args, tzinfo=UTC)


@pytest.fixture
def rng():
    return np.random.default_rng(0)
