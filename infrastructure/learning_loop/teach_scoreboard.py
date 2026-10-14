"""
Teach Translation OS scoreboard and manifest knowledge
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SCOREBOARD = BASE_DIR / "scoreboard" / "capability_scoreboard.json"
MANIFEST = BASE_DIR / "file_manifest.json"

ENC_PATH = BASE_DIR / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json"
MEM_REUSE_PATH = BASE_DIR / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json"
LEARNING_HISTORY_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_history.json"

def load_json(p):
    try:
        with open(p) as f:
            return json.load(f)
    except:
        return {}

def save_json(p, data):
    with open(p, "w") as f:
        json.dump(data, f, indent=2)

def teach_scoreboard():
    sb = load_json(SCOREBOARD)
    entries = []
    # Infrastructure
    for comp in sb.get("infrastructure", []):
        name = comp.get("component")
        if not name:
            continue
        definition = f"Infrastructure component: {name}. Role: {comp.get('role','')}. Status: {comp.get('status','')}"
        entries.append({"term": name.lower().replace(" ", "_"), "definition": definition, "category": "scoreboard"})
    # Components
    for comp in sb.get("components", []):
        name = comp.get("component")
        if not name:
            continue
        definition = f"Component: {name}. Status: {comp.get('status','')}. Reason: {comp.get('reason','')}"
        entries.append({"term": name.lower().replace(" ", "_"), "definition": definition, "category": "scoreboard"})
    # Pending
    for name in sb.get("pending", []):
        entries.append({"term": name.lower().replace(" ", "_"), "definition": f"Pending component: {name}", "category": "scoreboard"})
    return entries

def teach_manifest():
    mf = load_json(MANIFEST)
    entries = []
    for f in mf.get("files", []):
        filename = f.get("filename")
        purpose = f.get("purpose")
        if not filename:
            continue
        term = filename.replace("/", "_").replace(".", "_")
        definition = f"File: {filename}. Purpose: {purpose}"
        entries.append({"term": term.lower(), "definition": definition, "category": "manifest"})
    return entries

def populate_encyclopedia(entries):
    enc = load_json(ENC_PATH)
    if not isinstance(enc, list):
        enc = []
    existing = {e.get("term","").lower() for e in enc}
    added = 0
    for e in entries:
        if e["term"] not in existing:
            enc.append({
                "term": e["term"],
                "definition": e["definition"],
                "aliases": [],
                "category": e["category"]
            })
            added += 1
    save_json(ENC_PATH, enc)
    return added

def populate_memory_reuse(entries):
    mem = load_json(MEM_REUSE_PATH)
    if not isinstance(mem, list):
        mem = []
    added = 0
    for e in entries:
        query_signature = f"what is {e['term']} in translation os"
        mem.append({
            "query_signature": query_signature,
            "solution": e["definition"],
            "source": "teach_scoreboard_manifest",
            "category": e["category"]
        })
        added += 1
    save_json(MEM_REUSE_PATH, mem)
    return added

def populate_learning_history(entries):
    hist = load_json(LEARNING_HISTORY_PATH)
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
            "source": "teach_scoreboard_manifest"
        })
    hist["entries"] = entries_hist
    save_json(LEARNING_HISTORY_PATH, hist)

if __name__ == "__main__":
    sb_entries = teach_scoreboard()
    mf_entries = teach_manifest()
    all_entries = sb_entries + mf_entries
    enc_added = populate_encyclopedia(all_entries)
    mem_added = populate_memory_reuse(all_entries)
    populate_learning_history(all_entries)
    print(f"Scoreboard entries: {len(sb_entries)}")
    print(f"Manifest entries: {len(mf_entries)}")
    print(f"Encyclopedia added: {enc_added}")
    print(f"Memory Reuse added: {mem_added}")
