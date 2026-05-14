"""Track 2 event taxonomy and sector exposure mapping for S4."""

EVENT_TYPES: tuple[str, ...] = (
    "policy",
    "macro",
    "earnings",
    "commodity",
    "regulation",
    "liquidity",
    "risk",
    "other",
)

SECTOR_EXPOSURE_MAP: dict[str, tuple[str, ...]] = {
    "financial": ("512880.SH", "512800.SH", "512070.SH"),
    "bank": ("512800.SH",),
    "insurance": ("512070.SH",),
    "security": ("512880.SH",),
    "technology": ("159995.SZ", "159819.SZ", "515880.SH", "159852.SZ"),
    "semiconductor": ("159995.SZ",),
    "ai": ("159819.SZ",),
    "communication": ("515880.SH",),
    "software": ("159852.SZ",),
    "health": ("512010.SH", "512170.SH", "159992.SZ"),
    "pharma": ("512010.SH", "159992.SZ"),
    "consumption": ("515170.SH", "512690.SH"),
    "liquor": ("512690.SH",),
    "food": ("515170.SH",),
    "commodity": ("512400.SH", "515220.SH", "159870.SZ"),
    "metal": ("512400.SH",),
    "coal": ("515220.SH",),
    "chemical": ("159870.SZ",),
    "real_estate": ("512200.SH",),
    "property": ("512200.SH",),
}
