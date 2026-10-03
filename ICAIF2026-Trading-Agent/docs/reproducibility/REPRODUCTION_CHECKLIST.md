# Reproduction checklist

## Environment
- [ ] Python ≥ 3.11; `pip install -e '.[dev]'` (add `live` / `nlp` / `training` extras only when needed)
- [ ] `scripts/setup/fetch_official_kit.sh` at the pinned commit recorded in `official_adapter.PINNED_KIT_COMMIT`
- [ ] `ruff check src tests scripts` and `python -m pytest` green (official-kit parity tests not skipped)

## Data
- [ ] Every dataset has a manifest (`data/provenance.py`) and its hash appears in experiment records
- [ ] Raw files untouched in `data/raw/`; sources and terms recorded in `docs/data/DATA_PROVENANCE.md`
- [ ] Synthetic results are graded `synthetic_plumbing` and excluded from claims

## Models
- [ ] Each local model: id, revision, licence, weights sha256, download date, policy status
- [ ] `requires_rule_confirmation` resolved before any live use
- [ ] Fine-tuned artefacts carry `trained_through`; no model scores a decision before that date

## Experiments
- [ ] Run via `scripts/experiments/run_experiment.py` / `run_matrix.py` (never ad-hoc notebooks for claims)
- [ ] Record: experiment_id, git commit + dirty flag, dataset manifest, periods, config hash, seed, metrics
- [ ] Fee rate 0.001 (the engine refuses anything else for serious runs)
- [ ] NLP claims include no_news, shuffled, wrong_asset, random, sign_flip and stale ablations
- [ ] Walk-forward windows reported as distributions; locked final test read once

## Live
- [ ] Decision traces archived per round; no secrets (tested)
- [ ] Ledger + official checkpoint archived
- [ ] Final materials list matches the shared folder exactly
