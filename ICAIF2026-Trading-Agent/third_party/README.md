# third_party/

Git-ignored checkouts of external material that we reference but do not vendor.

- `icaif_starter_kit/` — the official ICAIF 2026 starter kit, fetched at a pinned commit by
  `scripts/setup/fetch_official_kit.sh`. `src/icaif/competition/official_adapter.py` imports it
  from here (or from `$ICAIF_KIT_ROOT`). Tests marked `official_kit` are skipped when it is absent.
