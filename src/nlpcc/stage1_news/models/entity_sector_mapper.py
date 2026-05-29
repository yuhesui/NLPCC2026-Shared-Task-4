"""Deterministic entity and sector mapping."""

from __future__ import annotations


SECTOR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "broad_equity": ("stock", "equity", "index", "shares", "a-share", "market", "沪深", "股市", "指数"),
    "technology": ("ai", "software", "semiconductor", "chip", "tech", "digital", "人工智能", "软件", "半导体", "芯片"),
    "healthcare": ("pharma", "healthcare", "medicine", "drug", "医药", "医疗", "创新药"),
    "consumer": ("consumer", "retail", "food", "beverage", "消费", "食品", "饮料"),
    "energy": ("energy", "coal", "oil", "power", "能源", "煤炭", "石油", "电力"),
    "materials": ("metal", "copper", "aluminum", "chemical", "材料", "有色", "化工"),
    "financials": ("bank", "securities", "insurance", "finance", "银行", "证券", "保险", "金融"),
    "real_estate": ("property", "real estate", "housing", "地产", "房地产", "楼市"),
    "gold": ("gold", "precious", "黄金", "贵金属"),
    "bonds": ("bond", "treasury", "rate cut", "yield", "债券", "国债", "利率", "降息"),
}


SECTOR_TO_TRACK2_ETFS: dict[str, tuple[str, ...]] = {
    "financials": ("512880.SH", "512800.SH", "512070.SH"),
    "securities": ("512880.SH",),
    "banking": ("512800.SH",),
    "insurance": ("512070.SH",),
    "technology": ("159995.SZ", "159819.SZ", "515880.SH", "159852.SZ"),
    "semiconductor": ("159995.SZ",),
    "ai": ("159819.SZ",),
    "communication": ("515880.SH",),
    "software": ("159852.SZ",),
    "healthcare": ("512010.SH", "512170.SH", "159992.SZ"),
    "pharma": ("512010.SH",),
    "innovative_drug": ("159992.SZ",),
    "consumer": ("515170.SH", "512690.SH"),
    "food_beverage": ("515170.SH",),
    "liquor": ("512690.SH",),
    "materials": ("512400.SH", "159870.SZ"),
    "nonferrous": ("512400.SH",),
    "chemicals": ("159870.SZ",),
    "energy": ("515220.SH",),
    "coal": ("515220.SH",),
    "real_estate": ("512200.SH",),
}


TRACK2_ETF_TO_SECTOR: dict[str, str] = {
    etf: sector
    for sector, etfs in {
        "securities": ("512880.SH",),
        "banking": ("512800.SH",),
        "insurance": ("512070.SH",),
        "semiconductor": ("159995.SZ",),
        "ai": ("159819.SZ",),
        "communication": ("515880.SH",),
        "software": ("159852.SZ",),
        "pharma": ("512010.SH",),
        "healthcare": ("512170.SH",),
        "innovative_drug": ("159992.SZ",),
        "food_beverage": ("515170.SH",),
        "liquor": ("512690.SH",),
        "nonferrous": ("512400.SH",),
        "coal": ("515220.SH",),
        "chemicals": ("159870.SZ",),
        "real_estate": ("512200.SH",),
    }.items()
    for etf in etfs
}


TRACK2_DETAIL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "securities": ("brokerage", "securities", "券商", "证券"),
    "banking": ("bank", "banking", "银行"),
    "insurance": ("insurance", "保险"),
    "semiconductor": ("semiconductor", "chip", "半导体", "芯片"),
    "ai": ("ai", "artificial intelligence", "人工智能", "算力"),
    "communication": ("communication", "telecom", "通信"),
    "software": ("software", "cloud", "软件", "数字化"),
    "pharma": ("pharma", "medicine", "医药", "生物医药"),
    "healthcare": ("healthcare", "medical", "医疗", "医疗保健"),
    "innovative_drug": ("innovative drug", "创新药"),
    "food_beverage": ("food", "beverage", "食品", "饮料"),
    "liquor": ("liquor", "baijiu", "白酒"),
    "nonferrous": ("nonferrous", "copper", "aluminum", "有色", "铜", "铝"),
    "coal": ("coal", "煤炭"),
    "chemicals": ("chemical", "chemicals", "化工"),
    "real_estate": ("real estate", "property", "房地产", "地产"),
}


ENTITY_ALIASES: dict[str, tuple[str, ...]] = {
    "PBOC": ("pboc", "central bank", "央行", "人民银行"),
    "State Council": ("state council", "国务院"),
    "CSRC": ("csrc", "证监会"),
    "Fed": ("fed", "federal reserve", "美联储"),
}


def normalize_text(text: str) -> str:
    return text.lower()


def map_text_to_sectors(text: str) -> tuple[str, ...]:
    lowered = normalize_text(text)
    sectors = [
        sector
        for sector, keywords in SECTOR_KEYWORDS.items()
        if any(keyword.lower() in lowered for keyword in keywords)
    ]
    sectors.extend(
        sector
        for sector, keywords in TRACK2_DETAIL_KEYWORDS.items()
        if any(keyword.lower() in lowered for keyword in keywords)
    )
    return tuple(sorted(set(sectors)))


def map_text_to_entities(text: str) -> tuple[str, ...]:
    lowered = normalize_text(text)
    entities = [
        entity
        for entity, aliases in ENTITY_ALIASES.items()
        if any(alias.lower() in lowered for alias in aliases)
    ]
    return tuple(sorted(set(entities)))


def map_sectors_to_track2_etfs(sectors: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    etfs: list[str] = []
    for sector in sectors:
        etfs.extend(SECTOR_TO_TRACK2_ETFS.get(sector, ()))
    return tuple(dict.fromkeys(etfs))


def map_track2_etf_to_sector(fund_id: str) -> str:
    return TRACK2_ETF_TO_SECTOR.get(fund_id, "unknown")
