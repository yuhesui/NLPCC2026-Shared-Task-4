# data/

Contents are git-ignored; only this README and `.gitkeep` files are tracked.

| Folder | Contents |
|---|---|
| `raw/` | source data exactly as retrieved (bars CSV, news JSONL, EDGAR JSON). Never edited in place. |
| `interim/` | cleaned / normalised intermediates |
| `processed/` | model-ready datasets (e.g. relevance pairs) |
| `cache/` | feature caches (content-addressed; safe to delete) |
| `manifests/` | dataset manifests (`icaif.data.provenance`) |

Formats and provenance rules: `docs/data/DATA_PROVENANCE.md`. Synthetic data is generated in memory
by `icaif.data.market.synthetic` and never written here as if it were real.
