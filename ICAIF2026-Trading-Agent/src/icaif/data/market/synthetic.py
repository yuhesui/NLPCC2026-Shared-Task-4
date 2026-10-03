"""Seeded SYNTHETIC market + news world for tests and plumbing smoke runs.

Nothing produced here is market data. Every bar/article carries
``source="synthetic"`` and every manifest ``synthetic=True``; the experiment
registry stamps results built on it as ``evidence_grade="synthetic_plumbing"``
so they can never be mistaken for research evidence.

Return model per bar (30-minute bars, 13 per session):
  r = beta * market + sector + idio + drift_i(t) + event impact
* ``drift_i`` is a slowly mean-reverting AR(1) per asset (gives momentum
  strategies something to find, at a controllable strength);
* planted events shock an asset's drift for a few hours; the companion news
  generator publishes an article about each event with configurable label
  noise, so the NLP plumbing can be tested end-to-end against a known truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import numpy as np

from icaif.core.schemas import Article, Provenance, content_hash
from icaif.core.time import et_datetime
from icaif.core.universe import SECTOR_OF, SECTORS, SYMBOLS
from icaif.data.market.panel import MarketPanel
from icaif.data.provenance import DatasetManifest, in_memory_manifest

SYNTHETIC_SOURCE = "synthetic"
_SECTOR_NAMES = tuple(SECTORS)

COMPANY_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "INTC": "Intel", "CRM": "Salesforce",
    "JPM": "JPMorgan", "BAC": "Bank of America", "GS": "Goldman Sachs", "V": "Visa", "PYPL": "PayPal",
    "LLY": "Eli Lilly", "JNJ": "Johnson & Johnson", "UNH": "UnitedHealth", "PFE": "Pfizer", "TMO": "Thermo Fisher",
    "AMZN": "Amazon", "TSLA": "Tesla", "WMT": "Walmart", "NKE": "Nike", "KO": "Coca-Cola",
    "CAT": "Caterpillar", "GE": "GE Aerospace", "BA": "Boeing", "XOM": "Exxon Mobil", "CVX": "Chevron",
    "GOOGL": "Alphabet", "META": "Meta Platforms", "DIS": "Disney", "T": "AT&T", "NEE": "NextEra Energy",
}

_POS_TEMPLATES = (
    "{name} raises full-year guidance after strong quarterly results",
    "{name} beats earnings estimates as demand accelerates",
    "Analysts upgrade {name} citing margin expansion",
    "{name} announces larger share buyback and dividend increase",
)
_NEG_TEMPLATES = (
    "{name} cuts outlook as demand weakens",
    "{name} misses earnings estimates on rising costs",
    "Regulators open investigation into {name}",
    "Analysts downgrade {name} on slowing growth",
)
_NOISE_TEMPLATES = (
    "Markets in focus: investors await central bank decision",
    "Stocks mixed as traders weigh economic data",
    "Oil prices steady ahead of inventory report",
)


@dataclass(frozen=True)
class SyntheticConfig:
    start: date = date(2026, 6, 1)
    days: int = 60
    bar_minutes: int = 30
    seed: int = 7
    start_price: float = 100.0
    market_vol_per_bar: float = 0.0025
    sector_vol_per_bar: float = 0.0015
    idio_vol_per_bar: float = 0.0030
    overnight_vol_mult: float = 3.0
    drift_persistence: float = 0.995
    drift_vol: float = 0.00005
    events_per_day: float = 1.5
    event_impact_per_bar: float = 0.0015
    event_duration_bars: int = 8
    news_label_noise: float = 0.2  # probability the article's tone is the WRONG sign
    noise_articles_per_day: float = 3.0
    availability_delay_seconds: int = 60


@dataclass(frozen=True)
class PlantedEvent:
    symbol: str
    published_at: datetime
    sign: int
    bar_index: int


@dataclass
class SyntheticWorld:
    panel: MarketPanel
    articles: list[Article]
    events: list[PlantedEvent]
    manifest: DatasetManifest
    config: SyntheticConfig = field(default_factory=SyntheticConfig)


def _business_days(start: date, count: int) -> list[date]:
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def generate_synthetic_world(config: SyntheticConfig | None = None) -> SyntheticWorld:
    cfg = config or SyntheticConfig()
    rng = np.random.default_rng(cfg.seed)
    n = len(SYMBOLS)
    days = _business_days(cfg.start, cfg.days)
    per_day = 390 // cfg.bar_minutes + (1 if 390 % cfg.bar_minutes else 0)
    sector_idx = np.array([_SECTOR_NAMES.index(SECTOR_OF[s]) for s in SYMBOLS])
    beta = rng.uniform(0.7, 1.3, n)
    drift = np.zeros(n)
    price = np.full(n, cfg.start_price) * rng.uniform(0.5, 3.0, n)

    starts: list[datetime] = []
    ends: list[datetime] = []
    o_rows, h_rows, l_rows, c_rows, v_rows = [], [], [], [], []
    events: list[PlantedEvent] = []
    event_shock = np.zeros(n)
    event_left = np.zeros(n, dtype=int)
    bar_counter = 0
    for d_idx, day in enumerate(days):
        session_open = et_datetime(day, "09:30")
        session_close = et_datetime(day, "16:00")
        # plant events for this day at random bar indices
        n_events = rng.poisson(cfg.events_per_day)
        planned = {}
        for _ in range(n_events):
            b = int(rng.integers(0, per_day))
            planned.setdefault(b, []).append((int(rng.integers(0, n)), int(rng.choice((-1, 1)))))
        for b in range(per_day):
            start = session_open + timedelta(minutes=b * cfg.bar_minutes)
            end = min(start + timedelta(minutes=cfg.bar_minutes), session_close)
            for j, sign in planned.get(b, []):
                # article published just before the bar starts; effect begins this bar
                events.append(PlantedEvent(SYMBOLS[j], start - timedelta(minutes=2), sign, bar_counter))
                event_shock[j] = sign * cfg.event_impact_per_bar
                event_left[j] = cfg.event_duration_bars
            vol_mult = cfg.overnight_vol_mult if (b == 0 and d_idx > 0) else 1.0
            market = rng.normal(0, cfg.market_vol_per_bar * vol_mult)
            sectors = rng.normal(0, cfg.sector_vol_per_bar * vol_mult, len(_SECTOR_NAMES))
            idio = rng.normal(0, cfg.idio_vol_per_bar * vol_mult, n)
            drift = cfg.drift_persistence * drift + rng.normal(0, cfg.drift_vol, n)
            active = event_left > 0
            ret = beta * market + sectors[sector_idx] + idio + drift + np.where(active, event_shock, 0.0)
            event_left = np.maximum(event_left - 1, 0)
            # open gaps on the first bar (overnight); intrabar path from open to close
            gap = ret * (0.6 if b == 0 and d_idx > 0 else 0.0)
            open_px = price * np.exp(gap)
            close_px = price * np.exp(ret)
            wiggle = np.abs(rng.normal(0, cfg.idio_vol_per_bar * 0.5, n))
            high_px = np.maximum(open_px, close_px) * np.exp(wiggle)
            low_px = np.minimum(open_px, close_px) * np.exp(-wiggle)
            volume = rng.lognormal(12.0, 0.4, n) * (1.0 + 4.0 * active)
            starts.append(start)
            ends.append(end)
            o_rows.append(open_px)
            h_rows.append(high_px)
            l_rows.append(low_px)
            c_rows.append(close_px)
            v_rows.append(volume)
            price = close_px
            bar_counter += 1

    delay = timedelta(seconds=cfg.availability_delay_seconds)
    panel = MarketPanel(
        starts=tuple(starts),
        ends=tuple(ends),
        available_at=tuple(e + delay for e in ends),
        open=np.array(o_rows),
        high=np.array(h_rows),
        low=np.array(l_rows),
        close=np.array(c_rows),
        volume=np.array(v_rows),
        bar_minutes=cfg.bar_minutes,
        source=SYNTHETIC_SOURCE,
        synthetic=True,
    )
    articles = _synthetic_articles(cfg, rng, events, days)
    manifest = in_memory_manifest(
        f"synthetic_world_seed{cfg.seed}_{cfg.days}d",
        "market_bars+news",
        {"config": cfg.__dict__, "close_hash": content_hash(panel.close.round(10).tobytes()), "articles": len(articles)},
        sources=(SYNTHETIC_SOURCE,),
        synthetic=True,
        rows=len(starts),
        start=starts[0].isoformat(),
        end=ends[-1].isoformat(),
    )
    return SyntheticWorld(panel=panel, articles=articles, events=events, manifest=manifest, config=cfg)


def _synthetic_articles(
    cfg: SyntheticConfig, rng: np.random.Generator, events: list[PlantedEvent], days: list[date]
) -> list[Article]:
    out: list[Article] = []
    for idx, event in enumerate(events):
        wrong = rng.random() < cfg.news_label_noise
        tone = -event.sign if wrong else event.sign
        template = rng.choice(_POS_TEMPLATES if tone > 0 else _NEG_TEMPLATES)
        title = str(template).format(name=COMPANY_NAMES[event.symbol])
        out.append(_article(f"evt{idx:05d}", title, f"({event.symbol}) {title}.", event.published_at, cfg))
    for d_idx, day in enumerate(days):
        for k in range(rng.poisson(cfg.noise_articles_per_day)):
            when = et_datetime(day, "08:00") + timedelta(minutes=int(rng.integers(0, 480)))
            title = str(rng.choice(_NOISE_TEMPLATES))
            out.append(_article(f"noise{d_idx:03d}_{k}", title, title + ".", when, cfg))
    out.sort(key=lambda a: a.available_at)
    return out


def _article(article_id: str, title: str, body: str, published_at: datetime, cfg: SyntheticConfig) -> Article:
    available = published_at + timedelta(seconds=cfg.availability_delay_seconds)
    return Article(
        article_id=article_id,
        title=title,
        body=body,
        source=SYNTHETIC_SOURCE,
        published_at=published_at,
        available_at=available,
        provenance=Provenance(SYNTHETIC_SOURCE, article_id, content_hash(title + body), retrieved_at=available),
        language="en",
    )
