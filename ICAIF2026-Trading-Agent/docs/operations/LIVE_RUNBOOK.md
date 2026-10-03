# Live runbook (Validation 2026-10-08..09, Official 2026-10-12..30)

All times ET. The organizer's live schedule and the official client are authoritative.

## 0. One-time setup

```sh
python -m venv .venv && . .venv/bin/activate
pip install -e '.[live,dev]'
scripts/setup/fetch_official_kit.sh                 # pinned commit; note if upstream moved
cp .env.example .env && chmod 600 .env             # CODABENCH_TOKEN, ICAIF_PROFILE
python -m pytest                                   # must be green, including official_kit parity tests
```

Registration (before **Oct 8 00:00 ET** to enter Validation) uses the official CLI directly. Run it
from this repository's root so it shares our `.icaif/` checkpoint and credentials:

```sh
KIT=third_party/icaif_starter_kit/starter-kit
python $KIT/tools/auto_submit.py --env .env --checkpoint .icaif/checkpoint.json \
    --credentials .icaif/credentials.json register --file private/register.json
```

The same `--env/--checkpoint/--credentials` flags apply to `schedule`, `portfolio`, `round`,
`resolve` and `fetch` below. The official session locks the checkpoint: never run the CLI and
`run_live.py` at the same time.

## 1. Pre-flight (each day)

1. `$KIT/tools/auto_submit.py --env .env --checkpoint .icaif/checkpoint.json --credentials .icaif/credentials.json schedule` — check for cancelled/early-close rounds; universe confirmed.
2. Data job is refreshing `data/raw/market/bars_30m.csv` (TODO(data): not bundled) — check the last bar
   is < 1 trading hour old during the session.
3. `python scripts/live/rehearse_paper.py --system <system>` — full loop offline.
4. Portfolio schema check (open question Q4): `auto_submit.py portfolio --phase validation`; confirm
   `icaif.competition.portfolio_state.parse_portfolio_payload` accepts it. If not, update the parser
   *before* running live (the runner holds on unknown shapes).

## 2. Run

```sh
# dry run against the real schedule/portfolio endpoints (never uploads)
python scripts/live/run_live.py --system configs/systems/q3_shrinkage_erc.yaml \
    --bars data/raw/market/bars_30m.csv --phase validation --mode dry_run --max-hours 8
# live uploads
python scripts/live/run_live.py ... --phase validation --mode live --confirm-live-uploads --max-hours 8
```

Per round the runner: reads the schedule (server clock) → finds the open window → skips if our ledger
already has the round, if < `safety_margin_seconds` (120 s) remain, or if the server shows the slot
consumed → reads our portfolio → freezes AS_OF → decides → writes the trace → HOLD (no upload) or
validates with both validators → claims the ledger → writes `private/decisions/<phase>/<round>/decision.json`
(0600) → `OriginalSession.decision()` uploads once.

## 3. Failure playbook

| Symptom | Action |
|---|---|
| Process crash / restart | Re-run the same command. Ledger + official checkpoint prevent a second upload; `AgentState` restores the daily turnover budget. |
| Ambiguous upload (network error after POST) | Do **not** re-upload. `auto_submit.py resolve`/`fetch` with the same checkpoint. |
| `HELD_PORTFOLIO_UNKNOWN` | Portfolio schema changed — fix parser; rounds hold meanwhile (no fee). |
| `stale_market_data` HOLDs | Fix the data job; holding is the safe default. |
| Fallback events in traces | Inspect `errors`; fallbacks are logged, not silent. `unexpected_exception` alerts need a code fix. |
| Need to stop trading | Stop the process: missing decisions hold. An all-zero decision liquidates (fees!) — only if intended. |

Never hand-edit weights: decisions must come from the registered agent logic.

## 4. After Official close (Oct 30 16:00 → Nov 3 23:59 ET)

Prepare final materials per kit `examples/final/README.md` and `disclosures.md`: source revision (git
commit), exact run command, configs, data-source/access records (DATA_PROVENANCE.md), model list with
revisions and policy status, LLM disclosure (none unless enabled; then model/version/provider/prompts/
settings from `outputs/traces/llm_calls.jsonl`), decision traces. One final slot only.
