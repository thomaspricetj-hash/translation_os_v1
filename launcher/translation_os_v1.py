"""
Translation OS v1 Launcher
Single executable pipeline integrating HSCL, Cache, Router
"""
import json
import re
from pathlib import Path
import subprocess
import sys
import signal
import atexit

def _flush_learning_state():
    """Auto-flush learning state on exit"""
    try:
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "learning_loop"))
        from learning_loop_v0 import analyze_patterns, update_weights
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "cache"))
        from auto_learn_cache_v1_1 import promote
        promote()
        analyze_patterns()
        update_weights()
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
# Register auto-flush on exit signals and normal exit
def _signal_handler(sig, frame):
    _flush_learning_state()
    sys.exit(0)
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)
atexit.register(_flush_learning_state)

CONFIG_PATH = BASE_DIR / "launcher" / "translation_os_v1_config.json"
CACHE_PATH = BASE_DIR / "infrastructure" / "cache" / "response_cache_v1_1.json"
HSCL_DICT_PATH = BASE_DIR / "infrastructure" / "hscl" / "hscl_dictionary_v1.json"
DICTIONARY_PATH = BASE_DIR / "infrastructure" / "dictionary" / "dictionary_v0.json"
ENCYCLOPEDIA_PATH = BASE_DIR / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json"
KNOWLEDGE_DICT_PATH = BASE_DIR / "infrastructure" / "knowledge" / "knowledge_dictionary_v0.json"
KNOWLEDGE_ENC_PATH = BASE_DIR / "infrastructure" / "knowledge" / "knowledge_encyclopedia_v0.json"
WORKSPACE_LOADER = BASE_DIR / "workspace_memory" / "workspace_memory_loader.py"
GPU_DETECTOR = BASE_DIR / "infrastructure" / "gpu_detector.py"

with open(CONFIG_PATH) as f:
    cfg = json.load(f)

# Load Workspace Memory V1
sys.path.insert(0, str(BASE_DIR / "workspace_memory"))
from workspace_memory_loader import load_workspace, log_journal, append_diary
WORKSPACE = load_workspace(task_id=None)
# Log session start
log_journal("Translation OS V1 session started")
append_diary("2026-10-13", "Workspace Memory V1 integrated into launcher startup")

# History Book V0 auto-logging
sys.path.insert(0, str(BASE_DIR / "history"))
from history_logger import log_history
# Example auto-log on startup - in production hook into scoreboard changes
log_history("Translation OS V1 session started", "milestone", "KEEP", "System startup with Master Orchestrator, Project Graph, Index Layer active")

# Auto-rebuild Index Layer V0 on startup if sources changed
sys.path.insert(0, str(BASE_DIR / "infrastructure" / "index"))
from index_builder import build_index
import json, os
index_path = BASE_DIR / "infrastructure" / "index" / "index_v0.json"
# Simple mtime check
source_paths = [
    BASE_DIR / "infrastructure" / "dictionary" / "dictionary_v0.json",
    BASE_DIR / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json",
    BASE_DIR / "infrastructure" / "cache" / "response_cache_v0.json",
    BASE_DIR / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json",
    BASE_DIR / "workspace_memory" / "diary.json",
    BASE_DIR / "workspace_memory" / "journal.json",
    BASE_DIR / "workspace_memory" / "project_book.json",
    BASE_DIR / "project_graph" / "project_graph_v0.json",
    BASE_DIR / "scoreboard" / "capability_scoreboard.json",
]
need_rebuild = True
if index_path.exists():
    index_mtime = index_path.stat().st_mtime
    latest_src = max((p.stat().st_mtime for p in source_paths if p.exists()), default=0)
    need_rebuild = latest_src > index_mtime
if need_rebuild:
    idx = build_index()
    with open(index_path, "w") as f:
        json.dump(idx, f, indent=2)
    log_journal("Index Layer V0 rebuilt on startup")
else:
    log_journal("Index Layer V0 up to date")

# Load HSCL dictionary
with open(HSCL_DICT_PATH) as f:
    hscl_dict_map = json.load(f)

# Load Dictionary Layer
with open(DICTIONARY_PATH) as f:
    dictionary_map = json.load(f)

# Load Encyclopedia Layer
with open(ENCYCLOPEDIA_PATH) as f:
    encyclopedia_entries = json.load(f)

def build_patterns(mapping):
    patterns = []
    for long_phrase, short in mapping.items():
        patterns.append((re.compile(r'\b'+re.escape(long_phrase)+r'\b', re.IGNORECASE), long_phrase, short))
    patterns.sort(key=lambda x: len(x[1]), reverse=True)
    return patterns

HSCL_PATTERNS = build_patterns(hscl_dict_map)
DICTIONARY_PATTERNS = build_patterns(dictionary_map)

def dictionary_normalize(text):
    res = text
    for pat, long_phrase, short in DICTIONARY_PATTERNS:
        def repl(m):
            mt = m.group(0)
            if mt.isupper():
                return short.upper()
            elif mt[0].isupper():
                return short.capitalize()
            else:
                return short
        res = pat.sub(repl, res)
    return res

def hscl_compress(text):
    res = text
    for pat, long_phrase, short in HSCL_PATTERNS:
        def repl(m):
            mt = m.group(0)
            if mt.isupper():
                return short.upper()
            elif mt[0].isupper():
                return short.capitalize()
            else:
                return short
        res = pat.sub(repl, res)
    return res

def canonicalize(text):
    t = text.lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# Simple cache lookup
def load_cache():
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}

cache_db = load_cache()

def find_cache_entry(query):
    canon = canonicalize(query)
    for qid, entry in cache_db.items():
        for pat in entry.get('patterns', []):
            if canonicalize(pat) == canon:
                return entry['answer']
    return None

# Simple router
MATH_INDICATORS = ["times","divided","percent","compute","multiply","learning rate"]
CODING_INDICATORS = ["python","write code","implement","function","bug","error","script"]
REASONING_INDICATORS = ["compare","analyze","explain","why","how does","difference between","summarize","role of"]
CONVERSATION_INDICATORS = ["hello","hi","thanks","opinion","tell me about","what is a"]

def classify(text):
    t = text.lower()
    if any(ind in t for ind in CODING_INDICATORS):
        return "Coding"
    if any(ind in t for ind in MATH_INDICATORS):
        return "Math"
    if any(ind in t for ind in REASONING_INDICATORS):
        return "Reasoning"
    if any(ind in t for ind in CONVERSATION_INDICATORS):
        return "Conversation"
    return "General"

def run_model(prompt):
    model_path = cfg['model']['gguf_path']
    llama_path = cfg['model']['llama_simple_path']
    max_tokens = cfg['model']['max_tokens']
    # Simple subprocess call - in production use proper API
    cmd = [llama_path, '-m', model_path, '-n', str(max_tokens), prompt]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        # Decode with utf-8 and replace errors to avoid cp1252 decode failures
        stdout_bytes = result.stdout if isinstance(result.stdout, bytes) else result.stdout.encode('utf-8', errors='replace')
        output = stdout_bytes.decode('utf-8', errors='replace')
        # Extract generated text from output
        # crude extraction
        lines = output.splitlines()
        # find first line after model output marker
        gen = []
        capture = False
        for line in lines:
            if 'decoded' in line.lower():
                break
            if capture:
                gen.append(line)
            if line.strip() and not line.startswith('llama') and not line.startswith('sched') and not line.startswith('~'):
                capture = True
        return '\n'.join(gen).strip()
    except Exception as e:
        return f"[Model error: {e}]"

def extract_term_from_query(text):
    t = text.lower().strip()
    prefixes = ["what is ", "define ", "explain ", "what does ", "who is "]
    for p in prefixes:
        if t.startswith(p):
            return t[len(p):].strip().strip('?')
    # fallback: return whole text
    return t

def encyclopedia_lookup(text):
    term_query = canonicalize(extract_term_from_query(text))
    for entry in encyclopedia_entries:
        term = canonicalize(entry.get('term',''))
        aliases = [canonicalize(a) for a in entry.get('aliases',[])]
        if term_query == term or term_query in aliases:
            return entry.get('definition','')
    return None

def knowledge_lookup_layer(text):
    import sys
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "knowledge"))
    from knowledge_lookup import knowledge_lookup as kl
    res = kl(text)
    return res

def memory_reuse_lookup(text):
    import sys
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "memory_reuse"))
    from memory_reuse_engine import reuse_lookup
    return reuse_lookup(text)

def reasoning_heatmap_lookup(text):
    import sys
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "reasoning_heatmap"))
    from reasoning_heatmap_v0 import reuse_heatmap
    return reuse_heatmap(text)

def problem_map(text):
    import sys
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "problem_mapper"))
    from problem_mapper_v0 import map_problem, format_for_model
    mapped = map_problem(text)
    if mapped["type"] in ["math", "coding", "comparison", "planning", "explanation"]:
        return format_for_model(mapped)
    return text

def problem_solve_plan(text):
    import sys
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "problem_solve"))
    from problem_solve_v0 import solve_problem
    # Simple type detection for demo
    t = text.lower()
    if "gpu" in t and "support" in t:
        ptype = "gpu_support"
    elif any(k in t for k in ["+", "-", "*", "/", "times", "calculate"]):
        ptype = "math"
    elif "python" in t or "code" in t or "fix" in t:
        ptype = "coding"
    else:
        ptype = "planning"
    plan = solve_problem(text, ptype)
    # Format plan for model context
    plan_str = f"[Problem Solve Plan] Type: {plan['problem_type']}; Goal: {plan.get('goal','')}; Steps: {', '.join(plan.get('steps',[]))}"
    return plan_str

def debate_layer(text):
    import sys
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "debate"))
    from debate_layer_v0 import debate
    t = text.lower()
    if "gpu" in t and "support" in t:
        ptype = "gpu_support"
    elif any(k in t for k in ["+", "-", "*", "/", "times", "calculate"]):
        ptype = "math"
    elif "python" in t or "code" in t or "fix" in t:
        ptype = "coding"
    else:
        ptype = "planning"
    result = debate(text, ptype)
    # Summarize for model context
    approaches_summary = " | ".join([f"{a['debater']}: {a['approach']}" for a in result['approaches']])
    debate_str = f"[Debate] Mode: {result['mode']}; Approaches: {approaches_summary}; Judge selected: {result['judge']['selected']['debater'] if result['judge']['selected'] else 'None'}"
    return debate_str

def process_query(query):
    # Abbreviation Dictionary V0 - normalize abbreviations first
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "abbreviation"))
    from abbreviation_lookup import normalize
    query_norm = normalize(query)
    # Master Orchestrator V0 - enforce priority order
    sys.path.insert(0, str(BASE_DIR / "orchestrator"))
    from master_orchestrator_v0 import run_orchestrator
    orch_result = run_orchestrator(query_norm)
    # Short-circuit if orchestrator found answer without model
    if orch_result.get("response_source") and orch_result.get("response_source") != "model":
        return {
            "source": orch_result.get("response_source"),
            "response": orch_result.get("response"),
            "orchestrator": orch_result,
            "short_circuit": True
        }
    # Project Graph V0 - get relevant components and blockers before reasoning
    sys.path.insert(0, str(BASE_DIR / "project_graph"))
    from graph_query import query_blockers, query_infrastructure
    project_blockers = query_blockers()
    project_infra = query_infrastructure()
    # Memory Reuse Layer - check before normalization to preserve signatures
    mem = memory_reuse_lookup(query)
    if mem:
        return {"source": mem["source"], "response": mem.get("solution") or mem.get("template"), "route": None, "memory_hit": True}
    
    # Index Layer V0 - instant lookup before full pipeline
    sys.path.insert(0, str(BASE_DIR / "infrastructure" / "index"))
    from index_lookup import lookup as index_lookup
    index_result = index_lookup(query)
    if index_result:
        # Log index hit
        log_journal(f"Index Layer hit for query: {query}")
        
    # Dictionary Layer
    dict_text = dictionary_normalize(query)
    
    # HSCL
    hscl_text = hscl_compress(dict_text) if cfg['pipeline']['hscl_enabled'] else dict_text
    
    # Canonicalizer
    # canonicalize is used downstream
    
    # Knowledge Layer
    know = knowledge_lookup_layer(hscl_text)
    if know:
        return {"source": know["source"], "response": know["response"], "route": None}
    
    # Encyclopedia Layer
    enc_def = encyclopedia_lookup(hscl_text)
    if enc_def:
        return {"source": "encyclopedia", "response": enc_def, "route": None}
    
    # Cache
    if cfg['pipeline']['response_cache_enabled']:
        cached = find_cache_entry(query)
        if cached:
            return {"source": "cache", "response": cached, "route": None}
    
    # Router
    route = classify(hscl_text) if cfg['pipeline']['router_enabled'] else "General"
    
    # Project Graph component selection and logging
    relevant_components = []
    if route == "Math":
        relevant_components = ["HSCL v1", "Response Cache v0", "Problem Mapper V0"]
    elif route == "Coding":
        relevant_components = ["HSCL v1", "Response Cache v0", "Problem Mapper V0"]
    elif route == "Reasoning":
        relevant_components = ["HSCL v1", "Reasoning Heatmap V0", "Problem Mapper V0"]
    else:
        relevant_components = ["HSCL v1", "Response Cache v0"]
    # Log selection to Workspace Memory
    log_journal(f"Project Graph selection for route {route}: {', '.join(relevant_components)}")
    append_diary("2026-10-13", f"Project Graph auto-selected components for {route} route: {', '.join(relevant_components)}")
    
    # Reasoning Heatmap
    heatmap = reasoning_heatmap_lookup(hscl_text)
    if heatmap:
        # Reuse successful reasoning path
        mapped_text = f"[Reasoning Heatmap Reuse] {hscl_text}"
    else:
        # Problem Mapper
        mapped_text = problem_map(hscl_text)
    
    # Problem Solve Layer V0 - generate explicit solution plan
    solve_plan = problem_solve_plan(mapped_text)
    mapped_text = f"{solve_plan}\n\n{mapped_text}"
    
    # Debate Layer V0 - generate multiple approaches
    debate_summary = debate_layer(mapped_text)
    mapped_text = f"{debate_summary}\n\n{mapped_text}"
    
    # Model
    response = run_model(mapped_text)
    return {"source": "model", "response": response, "route": route, "mapped": route in ["Math","Coding","Reasoning","Conversation"], "project_graph": {"blockers": project_blockers, "infrastructure": project_infra, "selected_components": relevant_components}, "index": index_result if index_result else None, "orchestrator": orch_result}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translation_os_v1.py 'your prompt here'")
        sys.exit(1)
    query = ' '.join(sys.argv[1:])
    result = process_query(query)
    # Learning Loop V0 - record solved problem for continuous improvement
    try:
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "learning_loop"))
        from learning_loop_v0 import record_problem, analyze_patterns, update_weights
        source = result.get("source")
        route = result.get("route")
        orchestrator = result.get("orchestrator", {})
        project_graph = result.get("project_graph", {})
        selected_components = project_graph.get("selected_components", [])
        # Build selected layers list from orchestrator diagnostics and components
        selected_layers = []
        if orchestrator.get("dictionary_hit"):
            selected_layers.append("Dictionary")
        if orchestrator.get("encyclopedia_hit"):
            selected_layers.append("Encyclopedia")
        if orchestrator.get("cache_hit"):
            selected_layers.append("Response Cache")
        if orchestrator.get("memory_reuse_hit"):
            selected_layers.append("Memory Reuse")
        if orchestrator.get("problem_mapper_hit"):
            selected_layers.append("Problem Mapper")
        if route in ["Math", "Coding", "Reasoning", "Conversation"]:
            selected_layers.append("Router")
        # Add project selected components
        selected_layers.extend(selected_components)
        # Reasoning path summary
        reasoning_path = {
            "orchestrator_source": orchestrator.get("response_source"),
            "route": route,
            "short_circuit": result.get("short_circuit", False)
        }
        # Simple success heuristic
        response_text = result.get("response", "")
        success_score = 0.0
        if source == "model" and "[Model error" not in response_text:
            success_score = 0.9
        elif source in ["cache", "encyclopedia", "dictionary", "memory_reuse"]:
            success_score = 1.0
        else:
            success_score = 0.5
        failure_score = 1.0 - success_score
        record_problem(query, selected_layers, reasoning_path, response_text[:500], success_score, failure_score)
        # Update patterns and weights
        analyze_patterns()
        update_weights()
        # Auto-learn cache from learning history
        try:
            sys.path.insert(0, str(BASE_DIR / "infrastructure" / "cache"))
            from auto_learn_cache_v1_1 import promote
            promote()
        except Exception:
            pass
    except Exception as e:
        # Non-fatal: learning loop should not break main pipeline
        log_journal(f"Learning Loop V0 error: {e}")
    print(json.dumps(result, indent=2))
