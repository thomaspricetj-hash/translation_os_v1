"""
Index Layer V0 Lookup
Instantly find memory, file, concept, project, journal entry, etc.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = BASE_DIR / "infrastructure" / "index" / "index_v0.json"

def load_index():
    with open(INDEX_PATH) as f:
        return json.load(f)

def lookup(query):
    idx = load_index()
    q = query.lower()
    results = {}
    # Search index metadata and source files for query term
    base = BASE_DIR
    # Map source names to paths
    source_paths = {
        "dictionary": base / "infrastructure" / "dictionary" / "dictionary_v0.json",
        "encyclopedia": base / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json",
        "response_cache": base / "infrastructure" / "cache" / "response_cache_v0.json",
        "memory_reuse": base / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json",
        "diary": base / "workspace_memory" / "diary.json",
        "journal": base / "workspace_memory" / "journal.json",
        "project_book": base / "workspace_memory" / "project_book.json",
        "project_graph": base / "project_graph" / "project_graph_v0.json",
        "scoreboard": base / "scoreboard" / "capability_scoreboard.json",
    }
    for src_name, path in source_paths.items():
        if not path.exists():
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            matches = []
            # Simple recursive search
            def search_obj(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if q in str(k).lower() or q in str(v).lower():
                            matches.append({k: v})
                        search_obj(v)
                elif isinstance(obj, list):
                    for item in obj:
                        search_obj(item)
            search_obj(data)
            if matches:
                results[src_name] = {
                    "file": str(path.relative_to(BASE_DIR)),
                    "matches": matches[:5]
                }
        except Exception:
            continue
    return results

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "gpu"
    print(json.dumps(lookup(q), indent=2))
