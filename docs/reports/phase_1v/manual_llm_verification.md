# Manual LLM Verification

## Prompt Export

Commands run:

```powershell
python scripts/export_llm_prompts.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-03 --run-id phase1v_manual_s2
python scripts/export_llm_prompts.py --track track1 --strategy s3_llm_alpha_tilt --config configs/track1/s3_llm_alpha_tilt.yaml --start-date 2024-01-02 --end-date 2024-01-03 --run-id phase1v_manual_s3
python scripts/export_llm_prompts.py --track track2 --strategy s4_event_exposure --config configs/track2/s4_event_exposure.yaml --start-date 2024-01-02 --end-date 2024-01-03 --run-id phase1v_manual_s4
```

Prompts were written under:

```text
.var/manual_llm/requests/<run_id>/
```

The generated prompts include required JSON schemas, prohibit allocation/trade output, and print the exact matching response path under:

```text
.var/manual_llm/responses/<run_id>/
```

Phase 1v removed stale `PLANNED - not implemented yet.` placeholder text from the LLM prompt templates and regenerated the inspected prompts.

## Pasted JSON Ingestion

A dummy valid S2 response was placed under `.var/manual_llm/responses/phase1v_manual_s2/20240102_track1_s2_llm_regime_regime.json`.

Command:

```powershell
python scripts/run_strategy.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-02 --llm-mode manual --run-id phase1v_manual_s2 --dry-run
```

Result: pass. The pasted JSON was accepted and produced normal `.var/runs/phase1v_manual_s2/` artifacts.

## Missing Response

Command:

```powershell
python scripts/run_strategy.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-02 --llm-mode manual --run-id phase1v_missing_s2 --dry-run
```

Result: expected failure. The error included the exact missing response path.

## Invalid Response

A malformed JSON file was placed under `.var/manual_llm/responses/phase1v_invalid_s2/20240102_track1_s2_llm_regime_regime.json`.

Command:

```powershell
python scripts/run_strategy.py --track track1 --strategy s2_llm_regime --config configs/track1/s2_llm_regime.yaml --start-date 2024-01-02 --end-date 2024-01-02 --llm-mode manual --run-id phase1v_invalid_s2 --dry-run
```

Initial result: failed to reject; S2 fell back to S1. Phase 1v fixed this defect by re-raising `ManualResponseInvalid` in manual mode for S2/S3/S4.

Final result: expected failure with `ManualResponseInvalid` and the invalid response path.

