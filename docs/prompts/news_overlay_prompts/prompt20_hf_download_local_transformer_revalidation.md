# Prompt20 — Explicit Hugging Face Download-Once Mode and Real Transformer Revalidation

## Role

You are a senior transformer systems engineer, Chinese financial NLP engineer, Hugging Face local-model integration engineer, GPU/cache engineer, and research-code reliability auditor.

You are continuing the News Overlay stage after the Prompt06.5–Prompt10 audit. The repo currently has transformer-first interfaces, proxy execution, cache traces, bounded grid runners, and safety checks, but **real local transformer inference is still blocked because no approved local model assets were configured**.

This prompt explicitly allows **Hugging Face download-once mode** for research cache preparation.

---

## Goal

Convert the News Overlay transformer methods from proxy-only evidence into real local-model evidence by explicitly downloading, pinning, caching, and validating approved Hugging Face models.

The goal is complete only if:

```text
1. approved model ids are selected and recorded;
2. downloads are explicit, logged, and non-silent;
3. models are cached locally;
4. later inference uses local_files_only=True;
5. N2/N3/N4/N5/N2345 and downstream I/S stacks run in no-proxy local-only mode where possible;
6. method/grid/status tables clearly distinguish real_model_executed, proxy_only, and blocked_missing_model;
7. no official runtime configs are changed;
8. no model binaries are added to official runtime packages.
```

---

## Important Policy Change

Previous prompts forbade **silent downloads**. This remains true.

This prompt now explicitly allows:

```text
download_once:
  allowed for approved Hugging Face model acquisition and local cache preparation.
```

Still forbidden:

```text
silent_download:
  forbidden

runtime_api_dependency:
  forbidden

automatic package inclusion of model binaries:
  forbidden

untracked or unpinned model download:
  forbidden
```

After download, all real transformer tests must run in:

```text
local_only mode
local_files_only=True
offline/no-API mode
```

---

## Default Hugging Face Cache

Assume the user’s default Hugging Face Hub cache is:

```text
C:\Users\jeanna\.cache\huggingface\hub
```

Also detect and report these environment variables if present:

```text
HF_HOME
HF_HUB_CACHE
TRANSFORMERS_CACHE
SENTENCE_TRANSFORMERS_HOME
NEWS_OVERLAY_LOCAL_MODELS
BGE_MODEL_PATH
FINBERT_MODEL_PATH
RERANKER_MODEL_PATH
```

If no override is set, treat the default Hugging Face cache path above as the expected download/cache location.

Do not copy model binaries into the repo.

---

## Recommended Model Targets

Select small-to-medium, reproducible models suitable for local research runs.

At minimum, try to configure:

```text
N2:
  Chinese or multilingual sentence embedding / BGE-style encoder

N3:
  Chinese financial sentiment / FinBERT-style classifier if available;
  otherwise use the embedding encoder for aspect-label similarity

N4:
  event-label encoder using the same embedding model if no specialised event model is available

N5:
  sector-query attention using N2 embeddings

N6:
  cross-encoder reranker if reasonably available;
  otherwise keep true cross-encoder blocked and use bi-encoder reranker proxy
```

Avoid very large models unless the repo explicitly supports them.

Record for each selected model:

```text
model_role
hf_model_id
revision_or_commit
license
expected_size
local_cache_path
dependency_requirements
download_status
load_status
device_used
notes
```

---

## Implementation Instructions

### 1. Read current state

Read the latest equivalent files:

```text
docs/news_overlay/method_table.md
docs/news_overlay/transformer_architecture_table.md
docs/news_overlay/grid_search_table.md
outputs/reports/news_overlay/prompt01_11/presented/prompt10_external_cross_check_summary.md
outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv
outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv
outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv
src/nlpcc/news_overlay/
configs/news_overlay/
tests/test_nlpcc/test_news_overlay/
```

Do not repeat documentation-only work.

---

### 2. Add explicit download mode

Add CLI/config support equivalent to:

```text
download-models --approved-models configs/news_overlay/approved_hf_models.yaml
check-models --offline
build-cache --method N2 --local-only
run --n-method N2345 --i-method I256 --s-method S126 --local-only
```

Exact command names may differ, but the workflow must exist.

Required modes:

```text
download_once:
  may access Hugging Face and download approved models.

local_only:
  must load from local cache/path only.

proxy_mode:
  remains available for infrastructure tests, but not counted as real transformer execution.
```

---

### 3. Create approved model config

Create/update:

```text
configs/news_overlay/approved_hf_models.yaml
configs/news_overlay/local_models.example.yaml
configs/news_overlay/local_models.local.example.yaml
```

`approved_hf_models.yaml` should contain only model metadata and approved download intent. Example schema:

```yaml
models:
  embedding_encoder:
    hf_model_id: "BAAI/bge-small-zh-v1.5"
    revision: "main"
    enabled: true
    purpose: "N2 embedding relevance, N4 labels, N5 sector-query attention"
  aspect_tone_encoder:
    hf_model_id: "<fill if suitable local/Chinese financial classifier is selected>"
    revision: "main"
    enabled: false
    purpose: "N3 aspect tone"
  reranker:
    hf_model_id: "<fill if selected>"
    revision: "main"
    enabled: false
    purpose: "N6 cross-encoder reranking"
```

Use exact model ids only after checking availability, size, and license.

---

### 4. Download and manifest

When downloading, record:

```text
network_attempted=true
download_user_approved=true
hf_model_id
revision_or_commit
local_cache_path
download_time
file_count
size_estimate
license
```

After download, switch back to local-only loading and record:

```text
network_attempted=false
local_files_only=True
```

Create:

```text
outputs/reports/news_overlay/prompt01_11/reference/hf_model_download_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/hf_model_download_manifest.md
outputs/reports/news_overlay/prompt01_11/reference/model_file_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv
```

---

### 5. Local-only loading pattern

Use a local-only loading pattern. Adapt the class to the model type.

Example pattern:

```python
import torch
from transformers import AutoTokenizer, AutoModel

local_model_path = r"C:\Users\jeanna\.cache\huggingface\hub\<resolved_model_snapshot_or_local_folder>"

tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)

device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModel.from_pretrained(
    local_model_path,
    local_files_only=True,
).to(device)

inputs = tokenizer("央行宣布降准释放长期流动性", return_tensors="pt", truncation=True).to(device)

with torch.no_grad():
    outputs = model(**inputs)

embedding = outputs.last_hidden_state.mean(dim=1)
print(embedding.shape)
```

If using a generative model only for a diagnostic smoke, the pattern may be:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

local_model_path = "./my_downloaded_model"

tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)

device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModelForCausalLM.from_pretrained(
    local_model_path,
    local_files_only=True,
    device_map="auto" if device == "cuda" else None,
)

inputs = tokenizer("Hello, how are you today?", return_tensors="pt").to(device)
outputs = model.generate(**inputs, max_new_tokens=50)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print(response)
```

For this News Overlay task, prefer encoder/classifier models over causal LLMs unless a causal model is explicitly selected for a specific diagnostic purpose.

---

### 6. Revalidate real transformer paths

Run no-proxy local-only validation for:

```text
N2
N3 or N3 proxy from real encoder
N4
N5
N12
N13
N2345
I5
I6
I256
S6
S126
```

Required smoke runs:

```text
check-models --offline
build-cache --method N2 --local-only --device auto
build-cache --method N3 --local-only --device auto
build-cache --method N4 --local-only --device auto
build-cache --method N5 --local-only --device auto

run --track A --n-method N2 --i-method I2 --s-method S3 --local-only --device auto
run --track B --n-method N2345 --i-method I256 --s-method S126 --local-only --device auto

run-grid --grid configs/news_overlay/grids/transformer_asset_smoke_grid.csv --local-only --device auto
```

Adapt command names to repo conventions and record exact commands.

---

## Tests

Add or update tests for:

```text
- approved download mode requires explicit config;
- unapproved model id is rejected;
- silent download is impossible in local_only mode;
- local_files_only=True is enforced after download;
- default cache path is detected or reported;
- N2 produces non-empty finite embeddings from real local model;
- N3 produces real or real-encoder-proxy aspect scores;
- N4 label scoring uses real local embeddings;
- N5 attention uses real local embeddings;
- N2345 writes component-level real/proxy status;
- cache keys include model id, revision/commit or snapshot path, preprocessing version, and text hash;
- second local-only run shows cache-hit behaviour;
- official runtime configs remain unchanged.
```

---

## Required Outputs

Create/update concise reports:

```text
outputs/reports/news_overlay/prompt01_11/progress/progress_20_hf_download_local_model_revalidation.md

outputs/reports/news_overlay/prompt01_11/presented/prompt20_hf_download_summary.md
outputs/reports/news_overlay/prompt01_11/presented/prompt20_local_transformer_revalidation.md

outputs/reports/news_overlay/prompt01_11/reference/hf_model_download_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/model_file_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv
outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv
outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv
outputs/reports/news_overlay/prompt01_11/reference/cache_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/error_log.md

docs/news_overlay/method_table.md
docs/news_overlay/transformer_architecture_table.md
docs/news_overlay/grid_search_table.md

docs/implementation_logs/<timestamp>_prompt20_hf_download_local_transformer_revalidation.md
```

Keep reports compact. Do not write huge model inventories into Markdown.

---

## Completion Gates

Do not mark complete unless:

```text
1. Hugging Face download policy is explicit and implemented.
2. Approved model ids are recorded.
3. Downloaded models are manifest-tracked.
4. Local-only loading uses local_files_only=True.
5. At least N2 runs with a real downloaded/local model, unless download fails with exact reason.
6. N2345 either runs with real/proxy component evidence or gives exact component block reasons.
7. Cache keys separate downloaded real models from proxy mode.
8. No official runtime config is changed.
9. Model binaries are not copied into the repo or package outputs.
10. Method and grid tables clearly distinguish real_model_executed from proxy_only.
```

---

## Do Not Do

```text
- Do not silently download.
- Do not download unapproved model ids.
- Do not run full 2024/2025 evaluation in this prompt.
- Do not promote candidates.
- Do not add model binaries to official runtime.
- Do not claim alpha improvement.
- Do not claim cross-encoder execution if only bi-encoder proxy ran.
```

---

## Final Response Format

```text
Prompt20 status:
  <pass/partial/fail>

HF download policy:
  <implemented/partial/failed>

Downloaded models:
  <list with ids, revisions, local paths>

Default cache path:
  C:\Users\jeanna\.cache\huggingface\hub

Real local model methods executed:
  <list>

Proxy-only methods remaining:
  <list>

Still blocked methods:
  <list with reason>

N2345 status:
  <real_executed / mixed_real_proxy / proxy_only / blocked / failed>

Cache status:
  <pass/partial/fail>

Smoke tests run:
  <commands and pass/fail>

Updated method table:
  <path>

Updated grid table:
  <path>

Should real no-proxy Prompt07 rerun next?
  <yes/no, with reason>

Most important remaining blocker:
  <specific blocker>
```
