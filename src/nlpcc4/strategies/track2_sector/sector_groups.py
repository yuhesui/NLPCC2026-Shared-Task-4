"""Track 2 sector grouping definitions."""

SECTOR_GROUPS: dict[str, tuple[str, ...]] = {
    "financials": ("512880.SH", "512800.SH", "512070.SH"),
    "technology": ("159995.SZ", "159819.SZ", "515880.SH", "159852.SZ"),
    "healthcare": ("512010.SH", "512170.SH", "159992.SZ"),
    "consumption": ("515170.SH", "512690.SH"),
    "materials_energy": ("512400.SH", "515220.SH", "159870.SZ"),
    "real_estate": ("512200.SH",),
}

ASSET_TO_GROUP: dict[str, str] = {
    asset: group for group, assets in SECTOR_GROUPS.items() for asset in assets
}
