# 2026-10-03 — first full matrix run (SYNTHETIC, plumbing only)

**Evidence grade: `synthetic_plumbing`.** Data: seeded synthetic world (`seed=7`, 60 business days,
30-minute bars, 25-day warm-up → 35 evaluation days = 245 rounds). The generator plants AR(1) drift
(so momentum "works" by construction) and news events with 20% label noise. Nothing here says
anything about real markets. Command: `python scripts/experiments/run_matrix.py` (77 experiments,
strict mode, 0 failures, 0 fallback rounds) plus the planted-signal family (12 experiments).

## What the run verified (code paths)

| Check | Observation |
|---|---|
| Cash control | Q0 cash: CR = MDD = turnover = 0 exactly |
| Fees bite | intraday momentum: 1h CR −24.9% (turnover 1.42/round), 2h −15.1%, 4h −5.6%, 1d −2.8%; 5d +7.3% (0.22), 20d +4.3% (0.10). At 0.1% per unit traded, horizons shorter than a day are destroyed by costs even with a planted drift. |
| Turnover controls matter | Q6 multi-horizon trend + ERC: unaware CR 3.14% / TO 0.091; strict sparse 3.85% / 0.034; rebalance R1+R4 only 4.19% / 0.052 |
| Exposure | fixed 80% and vol-target 10% cut MDD (0.061 → 0.049 / 0.036) at similar Sharpe; NLPCC-style 97% fixed is not special |
| Optimizer | Q7 (γ = 0.002, per-round/day caps) highest Sharpe with turnover 0.010 — on synthetic drift |
| Text ablations at default strength (impact 0.15%/bar, cap 2%) | no_news 0.26% ≈ zeroed 0.26%; full 0.23%; shuffled 0.03%, random 0.01%, sign_flip 0.08% — the full overlay did **not** beat no-news, the scrambled controls were worse |
| Overlay × turnover | overlay with turnover guard 0.48% (TO 0.0065) vs without 0.06% (TO 0.0141) |

## Planted-signal recovery (detection power)

Overlay cap 6% L1, label noise 10%:

| planted impact / bar | no_news CR | full CR | sign_flip CR | shuffled CR |
|---|---:|---:|---:|---:|
| 0.15% | +0.26% | +0.33% | −0.18% | −0.50% |
| 0.40% | +0.71% | +1.14% | −0.12% | −0.06% |
| 0.80% | +1.55% | +2.53% | +0.06% | +0.71% |

The pipeline recovers a known text signal and the gap grows with signal strength; sign-flipped and
shuffled text are always below no-news. The ablation machinery therefore has power to detect real
text value — on real data, the same comparison is the test that matters.

## Bugs found by this run

* Q6 (`score_tilt` with ERC anchor) never computed a covariance, so every round raised and the ERC
  fallback silently traded. Fixed (`PortfolioPipeline._needs_covariance`); research runs are now
  strict by default; matrix output flags any fallback rounds; a regression test runs every system
  config strictly.
