# Prompt16 Official Equivalence Report

Official server probe result: blocked, `Official server is not reachable at http://localhost:6207.` Prompt16 therefore did not claim new official-server equivalence. Local reference-vs-batched parity was verified.

| Strategy | Track | Window | Official Value | Reference Local Value | CUDA/Parallel Value | Official-Local Diff | Local-CUDA Diff | Trade Match | Status | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| S0 equal weight | macro | 20 dates smoke |  | 93340.456774 | 93340.456774 |  | `1.46e-11` | target replay match | blocked | Prompt14 official S0 parity remains the latest official evidence. |
| S1 quant core | macro | synthetic S1-like smoke |  |  | matched target replay |  | <= `1e-5` | target replay match | blocked | Prompt16 verifies replay semantics, not full agent-server parity. |
| S1 sector | sector | not run |  |  |  |  |  | not_run | blocked | Prompt14 official S1 sector parity remains the latest evidence. |
| DRO-BL-RP / robust BL | macro | not run |  |  |  |  |  | not_run | blocked | Official parity still required before promotion. |

Latest official evidence to preserve: Prompt14 reported S0 macro, S1 macro, and S1 sector parity pass. Prompt14 robust BL and sector rotation still had value/trade mismatches.
