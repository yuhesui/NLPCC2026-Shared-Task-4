# Prompt20.1 — Use Pre-Downloaded Hugging Face Models in Local-Only Mode

## Manual Pre-Step: Download Models Outside the Prompt

Run these commands yourself before executing Prompt20.1.

Default Hugging Face cache:

```powershell
$env:HF_HOME = "C:\Users\jeanna\.cache\huggingface"
$env:HF_HUB_CACHE = "C:\Users\jeanna\.cache\huggingface\hub"
```

Install / verify the CLI:

```powershell
python -m pip install -U huggingface_hub transformers sentence-transformers FlagEmbedding safetensors
hf version
hf env
```

Dry-run first:

```powershell
hf download BAAI/bge-small-zh-v1.5 --revision main --dry-run
hf download yiyanghkust/finbert-tone-chinese --revision main --dry-run
hf download IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment --revision main --dry-run
hf download BAAI/bge-reranker-v2-m3 --revision main --dry-run
```

Download the approved models:

```powershell
hf download BAAI/bge-small-zh-v1.5 --revision main
hf download yiyanghkust/finbert-tone-chinese --revision main
hf download IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment --revision main
hf download BAAI/bge-reranker-v2-m3 --revision main
```

Optional models:

```powershell
hf download BAAI/bge-base-zh-v1.5 --revision main
hf download BAAI/bge-reranker-base --revision main
hf download bardsai/finance-sentiment-zh-fast --revision main
```

After download, Prompt20.1 must use the models from local cache only.

---

# Prompt20.1 — Local-Only Validation Using Pre-Downloaded HF Models

## Role

You are a senior transformer systems engineer, Chinese financial NLP engineer, Hugging Face local-cache integration engineer, GPU/cache engineer, and research-code reliability auditor.

You are continuing after Prompt20. Hugging Face model download is handled manually before this prompt. Your job is **not** to download models. Your job is to make the repo use the already-downloaded Hugging Face models directly from local cache.

---

## Goal

Use the pre-downloaded Hugging Face models to convert the News Overlay transformer pipeline from proxy-only evidence into real local-model evidence.

The goal is complete only if:

```text
1. the repo detects the downloaded models in local cache;
2. model ids and local snapshot/cache paths are recorded;
3. inference uses local_files_only=True;
4. no network access occurs inside this prompt;
5. N2/N3/N4/N5/N2345 run with real local model evidence where possible;
6. method/grid tables distinguish real_model_executed, proxy_only, and blocked;
7. official runtime configs remain unchanged.
```

---

## Approved Models to Use

Use these model ids directly.

```yaml
embedding_encoder:
  hf_model_id: "BAAI/bge-small-zh-v1.5"
  revision: "main"
  enabled: true
  methods: [N2, N4, N5, N12, N2345]

financial_sentiment:
  hf_model_id: "yiyanghkust/finbert-tone-chinese"
  revision: "main"
  enabled: true
  methods: [N3, N13, I6, I256]

general_sentiment_fallback:
  hf_model_id: "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment"
  revision: "main"
  enabled: true
  methods: [N3_fallback]

reranker:
  hf_model_id: "BAAI/bge-reranker-v2-m3"
  revision: "main"
  enabled: true
  methods: [N6]
```

Optional models, only use if already downloaded and runtime is acceptable:

```yaml
embedding_encoder_larger_optional:
  hf_model_id: "BAAI/bge-base-zh-v1.5"
  revision: "main"
  enabled: false

reranker_fallback_optional:
  hf_model_id: "BAAI/bge-reranker-base"
  revision: "main"
  enabled: false

finance_news_sentiment_optional:
  hf_model_id: "bardsai/finance-sentiment-zh-fast"
  revision: "main"
  enabled: false
```

---

## Default Cache Location

Assume the downloaded models are under:

```text
C:\Users\jeanna\.cache\huggingface\hub
```

Also detect and report:

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

Do not copy model binaries into the repo.

---

## Instructions

### 1. Read current repo state

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

### 2. Configure local-only model use

Create/update:

```text
configs/news_overlay/approved_hf_models.yaml
configs/news_overlay/local_models.example.yaml
configs/news_overlay/local_models.local.example.yaml
```

These configs must map each approved `hf_model_id` to its local cache/snapshot path if detected.

Do not download anything in this prompt.

Required behaviour:

```text
network_attempted=false
local_files_only=True
download_allowed=false
```

If a model is missing, mark:

```text
blocked_missing_local_model
```

Do not silently fall back to proxy mode without recording it.

---

### 3. Use local-only loading

Use local-only loading patterns.

Encoder example:

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

Classifier example:

```python
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

local_model_path = r"C:\Users\jeanna\.cache\huggingface\hub\<resolved_model_snapshot_or_local_folder>"

tokenizer = AutoTokenizer.from_pretrained(local_model_path, local_files_only=True)

device = "cuda" if torch.cuda.is_available() else "cpu"

model = AutoModelForSequenceClassification.from_pretrained(
    local_model_path,
    local_files_only=True,
).to(device)

inputs = tokenizer("央行降准释放长期流动性", return_tensors="pt", truncation=True).to(device)

with torch.no_grad():
    logits = model(**inputs).logits

print(logits.softmax(dim=-1))
```

Reranker loading may use the model's recommended `FlagEmbedding` or `transformers` path, but it must still load from local cache only.

---

### 4. Revalidate target methods

Run no-proxy local-only validation for:

```text
N2
N3
N4
N5
N6 if reranker loads
N12
N13
N2345
I6
I256
S6
S126
```

Required commands or repo equivalents:

```text
check-models --local-only

build-cache --method N2 --local-only --device auto
build-cache --method N3 --local-only --device auto
build-cache --method N4 --local-only --device auto
build-cache --method N5 --local-only --device auto

run --track A --n-method N2 --i-method I2 --s-method S3 --local-only --device auto
run --track B --n-method N2345 --i-method I256 --s-method S126 --local-only --device auto

run-grid --grid configs/news_overlay/grids/transformer_asset_smoke_grid.csv --local-only --device auto
```

Do not run full 2024/2025 evaluation in this prompt.

---

## Tests

Add or update focused tests for:

```text
- approved model ids are recognised;
- local cache path is detected;
- local_only mode cannot download;
- local_files_only=True is enforced;
- N2 produces finite embeddings from BAAI/bge-small-zh-v1.5 if available;
- N3 produces classifier outputs from yiyanghkust/finbert-tone-chinese if available;
- fallback sentiment model status is explicit;
- N4/N5 use real local embeddings instead of proxy hash embeddings;
- N6 distinguishes true reranker from bi-encoder proxy;
- cache keys include hf_model_id, revision or resolved snapshot path, method code, preprocessing version, and text hash;
- official runtime configs remain unchanged.
```

---

## Required Outputs

Create/update concise artifacts:

```text
outputs/reports/news_overlay/prompt01_11/progress/progress_20_1_local_hf_model_use.md

outputs/reports/news_overlay/prompt01_11/presented/prompt20_1_local_model_use_summary.md
outputs/reports/news_overlay/prompt01_11/presented/prompt20_1_local_transformer_validation.md

outputs/reports/news_overlay/prompt01_11/reference/approved_hf_models.csv
outputs/reports/news_overlay/prompt01_11/reference/local_hf_model_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv
outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv
outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv
outputs/reports/news_overlay/prompt01_11/reference/cache_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/error_log.md

docs/news_overlay/method_table.md
docs/news_overlay/transformer_architecture_table.md
docs/news_overlay/grid_search_table.md

docs/implementation_logs/<timestamp>_prompt20_1_local_hf_model_use.md
```

Keep reports compact.

---

## Completion Gates

Do not mark complete unless:

```text
1. Approved HF model config exists.
2. Prompt does not download models.
3. Local-only loading uses local_files_only=True.
4. N2 either runs with BAAI/bge-small-zh-v1.5 or gives exact missing-cache reason.
5. N3 either runs with finbert-tone-chinese / fallback sentiment model or gives exact missing-cache reason.
6. N2345 has real/mixed/block component status.
7. Cache keys separate real local models from proxy mode.
8. Method and grid tables distinguish real_model_executed, proxy_only, and blocked.
9. Frozen official runtime remains unchanged.
```

---

## Do Not Do

```text
- Do not download models in this prompt.
- Do not silently download.
- Do not run full 2024/2025 evaluation.
- Do not promote candidates.
- Do not copy model binaries into the repo.
- Do not claim performance improvement.
- Do not claim true cross-encoder execution if only a bi-encoder proxy ran.
```

---

## Final Response Format

```text
Prompt20.1 status:
  <pass/partial/fail>

Approved models checked:
  <list>

Models found in local cache:
  <list>

Default HF cache:
  C:\Users\jeanna\.cache\huggingface\hub

Real local model methods executed:
  <list>

Proxy-only methods remaining:
  <list>

Blocked methods:
  <list with reason>

N2 status:
  <real_executed/proxy_only/blocked/failed>

N3 status:
  <real_executed/fallback_executed/proxy_only/blocked/failed>

N6 status:
  <true_reranker_executed/bi_encoder_proxy/blocked/failed>

N2345 status:
  <real_executed/mixed_real_proxy/proxy_only/blocked/failed>

Cache status:
  <pass/partial/fail>

Tests run:
  <commands and pass/fail>

Should rerun real no-proxy Prompt07 next?
  <yes/no, with reason>

Most important remaining blocker:
  <specific blocker>
```
