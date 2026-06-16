# Skill: nlpcc-evidence-ledger

## Purpose
Force every claim in reports and final responses to map to concrete evidence.

## When to use
Use in every NLPCC execution prompt that reads, writes, tests, evaluates, or reports.

## Required outputs
Create or update:

```text
presented/evidence_ledger.csv
```

Columns:

```text
claim_id
claim_text
claim_type
supporting_artifact
supporting_rows_or_lines
confidence
safe_to_report
unsafe_if_overstated
notes
```

## Rules
- No result claim without CSV/log/source evidence.
- If evidence is missing, write `not_evidenced`.
- Separate local public 2025 validation from official hidden evaluation.
- Never write `submission_ready` unless packaging and official submission requirements are completed.
