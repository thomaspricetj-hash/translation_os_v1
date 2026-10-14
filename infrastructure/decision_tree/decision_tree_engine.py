"""
Decision Tree V0 Engine
Chooses best path for solving request before invoking model
"""
import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def load_tree():
    path = BASE_DIR / "infrastructure" / "decision_tree" / "decision_tree_v0.json"
    with open(path) as f:
        return json.load(f)

def decide(query):
    # Decision Tree V0: choose cheapest correct path
    steps = [
        ("Dictionary", lambda q: False),  # placeholder
        ("Encyclopedia", lambda q: False),
        ("Response Cache", lambda q: False),
        ("Memory Reuse", lambda q: False),
        ("Rule Engine", lambda q: False),
        ("Problem Mapper", lambda q: False),
        ("Muse-Glimmer", lambda q: True)
    ]
    # Use Master Orchestrator for actual checks
    sys.path.insert(0, str(BASE_DIR / "orchestrator"))
    from master_orchestrator_v0 import run_orchestrator
    orch = run_orchestrator(query)
    return {
        "query": query,
        "path": orch.get("response_source"),
        "model_called": orch.get("model_called", False),
        "diagnostics": orch
    }

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is 2+2?"
    print(json.dumps(decide(q), indent=2))
