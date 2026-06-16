# Skill: leakage-split-auditor

## Purpose
Audit all split, feature, label, and evaluation logic for leakage.

## Checklist
- 2024 may be used for training/development only.
- 2025 public data may be used only as frozen evaluation.
- Hidden 2026 must never be accessed.
- Same-day close/high/low/return must not be used as decision-time features.
- Same-day news must respect official cutoff.
- Retrieval indexes for date `t` must not retrieve future news or future labels.
- Cache files must not silently mix 2024, 2025, and 2026 states.

## Required output
Create:

```text
presented/leakage_audit_summary.md
reference/leakage_audit_table.csv
```
