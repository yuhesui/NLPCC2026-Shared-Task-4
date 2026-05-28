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
    return tuple(sorted(set(sectors)))


def map_text_to_entities(text: str) -> tuple[str, ...]:
    lowered = normalize_text(text)
    entities = [
        entity
        for entity, aliases in ENTITY_ALIASES.items()
        if any(alias.lower() in lowered for alias in aliases)
    ]
    return tuple(sorted(set(entities)))
