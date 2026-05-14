# Manual LLM Workflow

## Generate Prompts

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python scripts/export_llm_prompts.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-03
```

Prompt files are written to:

```text
.var/manual_llm/requests/<run_id>/
```

Filenames use:

```text
YYYYMMDD_<track>_<strategy>_<decision_id>.md
```

## Paste Responses

Paste JSON-only model responses into:

```text
.var/manual_llm/responses/<run_id>/
```

Use the matching stem:

```text
YYYYMMDD_<track>_<strategy>_<decision_id>.json
```

The generated prompt file also prints the exact response path.

## Run With Pasted Responses

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
python scripts/run_strategy.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-03 --llm-mode manual
```

## Validation Behavior

- Responses are parsed from raw JSON or markdown JSON fences.
- S2 validates the regime schema.
- S3 validates the alpha-score schema.
- S4 validates the event-exposure schema.
- Missing manual responses fail with a clear path-specific error.
- Invalid responses are recorded in diagnostics or fall back to S1 when strategy policy allows it.
- Raw prompts and raw responses remain under `.var/` and must not be committed.
