# Official Server Spotcheck Report

Probe command:

`python scripts/run_official_server_smoke.py --output .var\prompt17\official_server_smoke.json`

Status: `blocked`.

Blocker: local official server unavailable at `http://localhost:6207` (`WinError 10061`, connection refused).

Local evidence uses the Prompt16 official-semantics reference and batched replay. No final selection evidence used `LocalSmokeBacktester`.
