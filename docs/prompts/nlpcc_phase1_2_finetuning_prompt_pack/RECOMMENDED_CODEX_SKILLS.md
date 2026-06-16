# Recommended Codex Skills for This Phase

OpenAI's Codex Agent Skills are task-specific instruction/resource packages. For this project, add skills only if they reduce repeated prompt burden and improve evidence discipline. Keep them local to the repo, versioned, and lightweight.

## Recommended skills to add

| Skill | Priority | Why add it |
|---|---:|---|
| `nlpcc-evidence-ledger` | High | Forces every claim to map to CSV/log/source evidence. |
| `leakage-split-auditor` | High | Checks 2024-only training, frozen 2025 evaluation, no hidden 2026, and cutoff-safe news use. |
| `presented-folder-packager` | High | Ensures `presented/` contains dense monitorable outputs rather than fragmented small files. |
| `local-hf-cache-provenance` | High | Verifies local-only model loading, cache identity, model hashes, and no network use. |
| `small-gpu-finetuning-runner` | Medium | Applies safe defaults for 6 GB RTX 4050 runs: short max length, gradient accumulation, fp16, tiny batches, early stop. |
| `official-parity-ablation-auditor` | High | Standardises official path checks, active/zeroed/shuffled ablations, no-proxy proof, and run CSV manifests. |

## Optional skills

| Skill | Priority | Why optional |
|---|---:|---|
| `cloud-gpu-run-manifest` | Medium | Useful if cloud 24–48 GB jobs are launched; records GPU type, driver, torch/CUDA, command, seed, wall-clock, and cost estimate. |
| `experiment-matrix-governor` | Medium | Prevents uncontrolled grid explosion; enforces bounded row counts and stop rules. |
| `system-report-claim-auditor` | Medium | Converts experimental results into safe system-report claims without overclaiming. |

## Do not add yet

| Skill | Reason |
|---|---|
| `rlhf-preference-optimizer` | Preference data is not strong enough yet. Use ranking/contrastive substitutes first. |
| `large-llm-finetuning` | Not aligned with current A2/B2 pipeline and risky under 6 GB local hardware. |
| `online-rag-agent` | Final inference path must remain local/offline; RAG here should be feature construction, not online generation. |
