# Fine-tuning plan (leakage-safe)

## Splits

Every training run declares a `TemporalSplit` (`backtest/walk_forward.py`):

```
train ──embargo── development ──embargo── locked validation ──embargo── final untouched test
```

* Segments are ordered, non-overlapping and embargoed (construction raises otherwise).
* Samples whose label window ends after a boundary are purged (`purge`, `assert_labels_before`).
* The final test is locked (`unlock_final_test` requires an explicit acknowledgement) and is read once.
* The ICAIF Validation/Official phases (Oct 2026) are never used for training or selection.
* Walk-forward: retrain at each step on data available *before* the step; every fitted artefact
  records `trained_through`, and `assert_model_cutoff` refuses to score earlier decisions with it.
* Every dataset (pairs, labels, features) gets a manifest (`data/provenance.py`) whose hash is stored
  in the experiment record.

## Stage A — representation adaptation (optional)

Domain-adaptive MLM / contrastive SimCSE on financial news and filings available before the
development period. Only if E1–E3 show a large gap between generic and finance-domain encoders.

## Stage B — event / relevance fine-tuning

Tasks: article↔company, article↔sector, article↔event class, event↔affected asset, article↔direction.
Labels: (1) entity-link weak labels (high-confidence cashtags / exchange tags / names);
(2) LLM-assisted labels from an allowed model on a sample, spot-checked by a human; (3) EDGAR 8-K item
codes as event-class labels (public, timestamped). Objectives: multiple-negatives ranking loss
(in-batch + mined hard negatives), triplet loss, supervised binary relevance, label-attention event
classification. Negatives: random company, same-sector, correlated company, market-wide, temporally
adjacent, stale repeat (`scripts/train/build_relevance_pairs.py`). Hard-negative mining is repeated per
epoch with the current model; the mining corpus is restricted to the training segment.

## Stage C — market-response supervision

Labels from prices *after* the article but strictly inside the training segment:
next-1h/1d/5d idiosyncratic return (residual to equal-weight index and sector), sector-adjusted
return, volatility response, abnormal volume, persistence horizon (time for |cum. abnormal return|
to peak). Models: ridge on aggregated text features (`models/text/linear.py`) first; then a small
head on frozen embeddings; only then end-to-end fine-tuning. Report IC by event type and horizon;
these estimates also replace the uncalibrated `configs/news/event_priors.yaml` half-lives.

## Leakage channels to control

1. Future prices in labels (purge + embargo).
2. Future articles in hard-negative mining or near-duplicate clusters (mine within segment only).
3. Model-selection on validation/test (only development is used for HPO).
4. **Pretrained model knowledge**: an LLM or encoder trained on text published after a backtest
   period can "know" outcomes. Record each model's stated training-data cutoff and run a
   post-cutoff-only evaluation slice; prefer evaluation periods after the model cutoff.
5. Revised data (macro vintages, amended filings) — use as-of vintages only.

## Compute and artefacts

Training lives under `scripts/train/`; checkpoints go to `models/` (git-ignored) with a manifest
(base model id + revision, data manifest hash, seed, hyper-parameters, `trained_through`).
No artefact is used live unless its base model's policy status is confirmed.

## Status

Pair builder, splits, purge, model-cutoff guard and ridge baseline are implemented and tested.
Stages A–C are **blocked on labelled real data and local base models**.
