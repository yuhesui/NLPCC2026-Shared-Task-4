# Skill: presented-folder-packager

## Purpose
Keep the `presented/` folder dense, monitorable, and not fragmented.

## Required structure
```text
presented/
  implementation_log.md
  progress_dashboard.md
  essential_results.md
  blockers_and_decisions.md
  run_csv/
  run_csv_manifest.csv
```

## Rules
- Put dense summaries in `essential_results.md`.
- Avoid many small Markdown files.
- All important CSVs must be copied into `presented/run_csv/`.
- `run_csv_manifest.csv` must explain why each CSV matters.
