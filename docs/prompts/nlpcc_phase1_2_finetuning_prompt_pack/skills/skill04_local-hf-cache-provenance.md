# Skill: local-hf-cache-provenance

## Purpose
Verify local-only Hugging Face model use and prevent silent downloads.

## Required checks
- `local_files_only=True`
- `network_attempted=False`
- local model path exists
- snapshot/hash recorded if available
- tokenizer path recorded
- device, dtype, batch size recorded
- sample output hash recorded

## Required output
```text
reference/local_model_asset_manifest.csv
presented/model_provenance_summary.md
```
