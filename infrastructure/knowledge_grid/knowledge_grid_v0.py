"""
Knowledge Grid V0
Weighted connections between Translation OS knowledge systems
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
GRID_PATH = BASE_DIR / "infrastructure" / "knowledge_grid" / "knowledge_grid_v0.json"

def load_grid():
    with open(GRID_PATH) as f:
        return json.load(f)

def find_related(node_id, top_n=5):
    grid = load_grid()
    edges = grid.get("edges", [])
    related = []
    for e in edges:
        if e["from"] == node_id or e["to"] == node_id:
            related.append({
                "node": e["to"] if e["from"] == node_id else e["from"],
                "relationship": e["relationship"],
                "weight": e["weight"],
                "source": e["source"]
            })
    # Sort by weight descending
    related.sort(key=lambda x: x["weight"], reverse=True)
    return related[:top_n]

def find_dependencies(node_id):
    grid = load_grid()
    deps = []
    for e in grid.get("edges", []):
        if e["to"] == node_id and e["relationship"] in ["depends_on", "blocks", "feeds"]:
            deps.append(e["from"])
    return deps

def find_blockers(node_id):
    grid = load_grid()
    blockers = []
    for e in grid.get("edges", []):
        if e["to"] == node_id and e["relationship"] == "blocks":
            blockers.append(e["from"])
    return blockers

def find_project_impacts(node_id):
    grid = load_grid()
    impacts = []
    for e in grid.get("edges", []):
        if e["from"] == node_id:
            impacts.append({"to": e["to"], "relationship": e["relationship"], "weight": e["weight"]})
    return impacts

if __name__ == "__main__":
    import sys
    node = sys.argv[1] if len(sys.argv) > 1 else "dictionary"
    print(json.dumps({
        "related": find_related(node),
        "dependencies": find_dependencies(node),
        "blockers": find_blockers(node),
        "impacts": find_project_impacts(node)
    }, indent=2))
