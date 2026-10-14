"""
Teach Translation OS workspace memory
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MEM_PATHS = [
    BASE_DIR / "workspace_memory" / "scratchpad.json",
    BASE_DIR / "workspace_memory" / "diary.json",
    BASE_DIR / "workspace_memory" / "journal.json",
    BASE_DIR / "workspace_memory" / "project_book.json",
]

ENC_PATH = BASE_DIR / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json"
MEM_REUSE_PATH = BASE_DIR / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json"
LEARNING_HISTORY_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_history.json"

def load_json(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except:
        return None

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ingest():
    entries = []
    for p in MEM_PATHS:
        if not p.exists():
            continue
        data = load_json(p)
        if data is None:
            continue
        name = p.stem
        if isinstance(data, dict):
            # create summary entry
            entries.append({
                "term": f"workspace_memory_{name}",
                "definition": f"Workspace memory file {name}: {json.dumps(data)[:500]}",
                "category": "workspace_memory"
            })
        elif isinstance(data, list):
            for i, item in enumerate(data[:20]):  # limit
                term = f"workspace_memory_{name}_{i}"
                entries.append({
                    "term": term,
                    "definition": f"Entry from {name}[{i}]: {json.dumps(item)[:400]}",
                    "category": "workspace_memory"
                })
    return entries

def populate_encyclopedia(entries):
    enc = load_json(ENC_PATH) or []
    existing = {e.get("term","").lower() for e in enc}
    added = 0
    for e in entries:
        if e["term"] not in existing:
            enc.append({"term": e["term"], "definition": e["definition"], "aliases": [], "category": e["category"]})
            added += 1
    save_json(ENC_PATH, enc)
    return added

def populate_memory_reuse(entries):
    mem = load_json(MEM_REUSE_PATH) or []
    added = 0
    for e in entries:
        query_signature = f"what is {e['term']} in translation os"
        mem.append({"query_signature": query_signature, "solution": e["definition"], "source": "teach_workspace_memory", "category": e["category"]})
        added += 1
    save_json(MEM_REUSE_PATH, mem)
    return added

def populate_learning_history(entries):
    hist = load_json(LEARNING_HISTORY_PATH) or {"entries": []}
    entries_hist = hist.get("entries", [])
    for e in entries:
        entries_hist.append({
            "timestamp": "2026-10-13T00:00:00Z",
            "problem": f"What is {e['term']} in Translation OS?",
            "selected_layers": ["Encyclopedia", "Memory Reuse"],
            "reasoning_path": {"orchestrator_source": "memory_reuse", "route": "General"},
            "answer": e["definition"][:500],
            "success_score": 1.0,
            "failure_score": 0.0,
            "source": "teach_workspace_memory"
        })
    hist["entries"] = entries_hist
    save_json(LEARNING_HISTORY_PATH, hist)

if __name__ == "__main__":
    entries = ingest()
    enc_added = populate_encyclopedia(entries)
    mem_added = populate_memory_reuse(entries)
    populate_learning_history(entries)
    print(f"Workspace memory entries ingested: {len(entries)}")
    print(f"Encyclopedia added: {enc_added}")
    print(f"Memory Reuse added: {mem_added}")
