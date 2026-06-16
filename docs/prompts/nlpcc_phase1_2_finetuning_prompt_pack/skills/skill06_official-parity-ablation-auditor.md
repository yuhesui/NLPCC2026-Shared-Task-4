# Skill: official-parity-ablation-auditor

## Purpose
Standardise official path checks and news-use proof.

## Required ablations
- active news
- zeroed news
- date-shuffled news
- random labels
- trained module disabled
- proxy attempt should block
- model disabled should block

## Required output
```text
presented/run_csv/ablation_results.csv
presented/ablation_interpretation.md
reference/official_path_manifest.csv
```

## Interpretation
- If active equals zeroed, the module is not materially used.
- If shuffled beats active, do not claim real news value.
- If proxy attempts are not blocked, production path is unsafe.
