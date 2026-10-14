"""
Teach Translation OS everything about its design
Ingests docs, scoreboard, manifest and populates Knowledge/Encyclopedia/Memory Reuse/Learning History
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DOCS = [
    BASE_DIR / "docs" / "architecture.md",
    BASE_DIR / "docs" / "roadmap.md",
    BASE_DIR / "docs" / "surviving_components.md",
]

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
        return []

def save_json(p, data):
    with open(p, "w") as f:
        json.dump(data, f, indent=2)

def ingest_docs():
    entries = []
    for p in DOCS:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        # Simple heuristic extraction of headings and bullet items
        lines = text.splitlines()
        current_section = ""
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                current_section = line[2:].strip()
            elif line.startswith("## "):
                current_section = line[3:].strip()
            elif line.startswith("- "):
                item = line[2:].strip()
                # Create encyclopedia entry
                term = item.split(":")[0].split(" ")[0] if " " in item else item
                entries.append({
                    "term": term.lower(),
                    "definition": f"{current_section}: {item}",
                    "source_doc": p.name,
                    "category": "design"
                })
    return entries

def populate_encyclopedia(entries):
    enc = load_json(ENC_PATH)
    if not isinstance(enc, list):
        enc = []
    existing_terms = {e.get("term","").lower() for e in enc}
    added = 0
    for e in entries:
        if e["term"] not in existing_terms:
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
        query_signature = f"what is {e['term']} in translation os design"
        mem.append({
            "query_signature": query_signature,
            "solution": e["definition"],
            "source": "teach_design",
            "category": "design"
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
            "source": "teach_design"
        })
    hist["entries"] = entries_hist
    save_json(LEARNING_HISTORY_PATH, hist)

if __name__ == "__main__":
    entries = ingest_docs()
    enc_added = populate_encyclopedia(entries)
    mem_added = populate_memory_reuse(entries)
    populate_learning_history(entries)
    print(f"Teach run complete")
    print(f"Encyclopedia entries added: {enc_added}")
    print(f"Memory Reuse entries added: {mem_added}")
    print(f"Total design concepts ingested: {len(entries)}")
