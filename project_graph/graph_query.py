"""
Project Graph V0 Query Interface
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_PATH = BASE_DIR / "project_graph" / "project_graph_v0.json"

def load_graph():
    with open(GRAPH_PATH) as f:
        return json.load(f)

def query_depends_on(component_name):
    g = load_graph()
    results = []
    for e in g.get("edges", []):
        if e.get("type") == "depends_on" and e.get("target") == component_name:
            results.append(e.get("source"))
    return results

def query_blockers():
    g = load_graph()
    blockers = []
    for n in g.get("nodes", []):
        if n.get("status") == "BLOCKED":
            blockers.append(n.get("name"))
    return blockers

def query_infrastructure():
    g = load_graph()
    return [n["name"] for n in g.get("nodes", []) if n.get("type") == "Infrastructure" and n.get("status") == "KEEP"]

def query_next_candidates():
    g = load_graph()
    candidates = []
    for n in g.get("nodes", []):
        if n.get("status") in ["PENDING", "IN_PROGRESS"]:
            candidates.append(n.get("name"))
    return candidates

if __name__ == "__main__":
    g = load_graph()
    print("Infrastructure:", query_infrastructure())
    print("Blockers:", query_blockers())
    print("Next candidates:", query_next_candidates())
