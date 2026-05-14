# Phase 1v Known Issues

## Blocking

None for Phase 1b entry.

## Important Non-Blocking

- Official server/demo smoke was not run because `fastapi` is missing in the active environment.
- Public official CSV data is absent in this checkout, so dry-runs used the deterministic official-compatible synthetic loader.
- Same-day news semantics need concrete official-data examples. Status: unresolved; conservative default is `previous_day_only`.
- Trade converter still needs reconciliation against an official server session because the official engine updates holdings by same-day return before executing same-day close trades.
- Metrics should be compared against official result parsing on a small official-server run once server dependencies are installed.

## Optional

- Broaden dry-runs across longer 2024 windows.
- Add Track 2 manual pasted-response round-trip checks for S3/S4.
- Add more diagnostics summarizing fallback counts across full windows.
