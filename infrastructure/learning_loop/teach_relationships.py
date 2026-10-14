"""
Teach Translation OS design relationships via Q&A pairs
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MEM_REUSE_PATH = BASE_DIR / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json"
LEARNING_HISTORY_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_history.json"

QA_PAIRS = [
    {
        "q": "What is the pipeline order for Translation OS v1?",
        "a": "Raw Text → HSCL v1 → HSCL Extensions → Canonicalizer → Response Cache → Router → Muse-Glimmer"
    },
    {
        "q": "Which components are blocked and why?",
        "a": "Math-Boost v1 is blocked because it requires GPU LoRA training infrastructure not available in current environment"
    },
    {
        "q": "What is scoreboard RULE 0?",
        "a": "Components must survive compression/accuracy/latency gates to be KEEP"
    },
    {
        "q": "What is scoreboard RULE 1?",
        "a": "KEEP components become frozen infrastructure and are no longer re-evaluated every cycle. Only regressions can remove them"
    },
    {
        "q": "What is the relationship between HSCL v1 Response Cache v0 and Prompt Classifier Router v0?",
        "a": "HSCL v1 compresses prompts before inference, Response Cache v0 short-circuits deterministic answers before model, Prompt Classifier Router v0 routes prompts to appropriate handling. Order is HSCL → Cache → Router → Muse-Glimmer"
    },
    {
        "q": "Why is Math-Boost v1 blocked?",
        "a": "Math-Boost v1 requires GPU LoRA training infrastructure which is not available. Status is BLOCKED not FAILED"
    },
    {
        "q": "What is the compression delta for HSCL v1?",
        "a": "HSCL v1 provides +29.9% compression with ~0% accuracy loss and +0.08ms latency"
    },
    {
        "q": "Which components survived scoreboard evaluation?",
        "a": "HSCL v1, HSCL Word Reuse v1, HSCL Semantic Grouping v0, Response Cache v0, Prompt Classifier Router v0 are INFRASTRUCTURE. Math-Boost v1 is BLOCKED"
    },
    {
        "q": "What is the role of Response Cache v0?",
        "a": "Response Cache v0 provides deterministic answer caching with question canonicalization to avoid model inference for repeated questions"
    },
    {
        "q": "What is the role of Prompt Classifier Router v0?",
        "a": "Prompt Classifier Router v0 performs rule-based prompt routing into Math, Coding, Reasoning, Conversation, General"
    }
]

def load_json(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except:
        return []

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def teach():
    mem = load_json(MEM_REUSE_PATH) or []
    hist = load_json(LEARNING_HISTORY_PATH) or {"entries": []}
    entries_hist = hist.get("entries", [])
    
    added_mem = 0
    for pair in QA_PAIRS:
        q = pair["q"]
        a = pair["a"]
        # Normalize signature
        sig = q.lower()
        # Check if already exists
        exists = any(m.get("query_signature") == sig for m in mem)
        if not exists:
            mem.append({
                "query_signature": sig,
                "solution": a,
                "source": "teach_relationships",
                "category": "relationships"
            })
            added_mem += 1
        
        entries_hist.append({
            "timestamp": "2026-10-13T00:00:00Z",
            "problem": q,
            "selected_layers": ["Memory Reuse", "Encyclopedia"],
            "reasoning_path": {"orchestrator_source": "memory_reuse", "route": "General"},
            "answer": a,
            "success_score": 1.0,
            "failure_score": 0.0,
            "source": "teach_relationships"
        })
    
    save_json(MEM_REUSE_PATH, mem)
    save_json(LEARNING_HISTORY_PATH, hist)
    return len(QA_PAIRS), added_mem

if __name__ == "__main__":
    total, added = teach()
    print(f"Relationship Q&A pairs taught: {total}")
    print(f"Memory Reuse entries added: {added}")
