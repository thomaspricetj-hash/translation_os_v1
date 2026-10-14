# Translation OS v1

Translation OS v1 is a modular inference operating system for language models. It adds infrastructure layers around a base LLM — Muse-Glimmer — to reduce unnecessary model calls, improve memory efficiency, and provide persistent project memory.

## Architecture Overview

```
Raw Text
  ↓
Index Layer
  ↓
Dictionary Layer
  ↓
HSCL v1
  ↓
Canonicalizer
  ↓
Encyclopedia Layer
  ↓
Response Cache
  ↓
Memory Reuse Layer
  ↓
Problem Mapper
  ↓
BD3D Hybrid Compression
  ↓
Decision Tree / Roundabout Router
  ↓
Master Orchestrator
  ↓
Muse-Glimmer
```

Additional systems:
* **Workspace Memory V1** – Scratchpad, Diary, Journal, Project Book, History Book, Future Book
* **DAX KV-Delta Engine V0** – Master/Delta KV cache with instant rollback and branching
* **BD3D Hybrid Compression V0** – DAX Token Layer + BitDrop hybrid compression for storage
* **Fractal Agent System** – Tagged agents with shared scratchpad and merge engine
* **Reasoning System** – Problem Mapper, Problem Solve Layer, Debate Layer, Reasoning Heatmap, Knowledge Grid, Weave Layer
* **Policy & Weighting** – Policy Layer, Memory Weight, Confidence Weight, Relevance Engine, Adaptive Reasoning Weights

## Quick Start

```bash
cd TRANSLATION_OS_V1
python launcher/translation_os_v1.py --query "What is 2+2?"
```

Config: `launcher/translation_os_v1_config.json`

## How to Use

### Basic query
```python
from launcher.translation_os_v1 import TranslationOS
os = TranslationOS()
answer = os.ask("What is the definition of entropy?")
print(answer)
```

### Pipeline diagnostics
The Master Orchestrator logs which layers were activated:
```json
{
  "index_hit": false,
  "dictionary_hit": false,
  "encyclopedia_hit": true,
  "cache_hit": false,
  "model_called": false,
  "response_source": "encyclopedia"
}
```

### Adding new knowledge
**Dictionary**
Edit `infrastructure/dictionary/dictionary_v0.json`:
```json
{"automobile": "car"}
```

**Encyclopedia**
Edit `infrastructure/encyclopedia/encyclopedia_v0.json`:
```json
{"term":"api","definition":"Application Programming Interface","category":"software"}
```

**Response Cache**
Cache is automatic. To pre-seed:
```json
{"question":"What is 2+2?","answer":"4"}
```

## Adding Different Models

Translation OS is model-agnostic. The model is loaded via `models/active_model.json`.

### 1. Prepare model files
Place GGUF file in `models/`:
```
models/Muse-Glimmer-Dequantized-Q4_K_M-real.gguf
```

### 2. Update active_model.json
```json
{
  "model_name": "Muse-Glimmer",
  "model_path": "models/Muse-Glimmer-Dequantized-Q4_K_M-real.gguf",
  "backend": "llama.cpp",
  "infrastructure": ["HSCL v1","Response Cache v0","..."]
}
```

### 3. Add model-specific config
For llama.cpp backend, set in `launcher/translation_os_v1_config.json`:
```json
{
  "gpu_mode": "auto",
  "cpu_fallback": true,
  "n_gpu_layers": "auto",
  "model_path": "models/Muse-Glimmer-Dequantized-Q4_K_M-real.gguf"
}
```

### 4. WeaveFormer model
To use WeaveFormer:
```bash
cd infrastructure/training/weaveformer
python automate_training_pipeline.py --config weaveformer/config-5b.json --model_name weave-5b --quantize
```
Then update `active_model.json` to point to the new GGUF and set `"model_arch": "weave"`.

### 5. PyTorch backend with DAX KV-Delta
If using PyTorch backend, enable DAX KV-Delta Engine:
```json
{
  "kv_cache_engine": "dax_kv_delta",
  "dax_master_kv": true,
  "dax_branching": true
}
```
The DAX KV-Delta Engine provides instant rollback and multi-agent overlays.

## Infrastructure Components

### Knowledge
* Dictionary Layer V0 – synonym/abbreviation normalization
* Abbreviation Dictionary V0 – acronym expansion
* Encyclopedia Layer V0 – concept definitions
* Knowledge Layer V0 – word meanings + relationships

### Memory
* Workspace Memory V1 – Scratchpad, Diary, Journal, Project Book
* History Book V0, Future Book V0
* Memory Reuse Layer V0 – solved problems and reasoning templates
* Response Cache V0 / V1.1 with auto-learn

### Reasoning
* Problem Mapper V0 – classify math/coding/planning
* Problem Solve Layer – generate solution plans
* Debate Layer – multi-approach reasoning
* Reasoning Heatmap – track importance
* Decision Tree V0, Roundabout Router V0
* Master Orchestrator V0 – cheapest-correct-path routing

### Compression & Efficiency
* HSCL v1 – semantic compression +29.9%
* HSCL Word Reuse v1, HSCL Semantic Grouping v0
* BD3D Hybrid Compression V0 – DAX Token Layer + BitDrop for storage
* DAX KV-Delta Engine V0 – KV-cache delta memory

### Agents & Workspace
* Fractal Agent System V0 – tagged agents with shared scratchpad
* Sandbox + Workspace V0 – safe experiments vs persistent work
* Project Graph V0, Knowledge Grid, Weave Layer

## Scoreboard

KEEP/DELETE decisions are tracked in `scoreboard/capability_scoreboard.json`.

Rules:
* RULE 0: Component must survive compression/accuracy/latency gates to be KEEP
* RULE 1: KEEP components become frozen infrastructure

## Adding New Infrastructure

1. Create component under `infrastructure/<name>/`
2. Add helper + micro-helper files
3. Update `file_manifest.json`
4. Run validation and update `scoreboard/capability_scoreboard.json`
5. Wire into Master Orchestrator priority order

Example entry:
```json
{
  "component": "MyLayer V0",
  "role": "Description",
  "status": "KEEP",
  "promoted_date": "2026-10-14"
}
```

## Testing

```bash
python reports/end_to_end_test_hard_question.py
python infrastructure/dax_kv_delta/dax_kv_delta_benchmark.py
```

## License

Translation OS v1 core is proprietary. Components marked MIT, e.g., BD3D Hybrid Compression, may be used per their licenses. DAX KV-Delta Engine is evaluation-only per TEL-1.0 unless commercial license obtained.

## Support

See `workspace_memory/project_book.json` for current project state and `workspace_memory/future_book.json` for roadmap.
