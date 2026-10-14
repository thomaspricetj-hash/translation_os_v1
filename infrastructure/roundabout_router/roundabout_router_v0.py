"""
Roundabout Router V0
Evaluates multiple execution paths and selects best route
"""
import json
from pathlib import Path
import sys

BASE = Path("TRANSLATION_OS_V1")
HISTORY_FILE = BASE / "infrastructure" / "roundabout_router" / "route_history.json"
REPORT_FILE = BASE / "infrastructure" / "roundabout_router" / "roundabout_router_report.json"

sys.path.insert(0, str(BASE / "infrastructure" / "roundabout_router"))
from route_score_engine import evaluate_routes

def load_json(p):
    try:
        return json.load(open(p))
    except:
        return {}

def save_json(p, data):
    with open(p, "w") as f:
        json.dump(data, f, indent=2)

def route_query(query, diagnostics):
    scored = evaluate_routes(query, diagnostics)
    best = scored[0] if scored else {"route": "Muse-Glimmer", "score": 0.5}
    
    # Record history
    history = load_json(HISTORY_FILE)
    history.setdefault("history", []).append({
        "query": query,
        "scored_routes": scored,
        "selected_route": best["route"],
        "selected_score": best["score"]
    })
    save_json(HISTORY_FILE, history)
    
    return {
        "selected_route": best["route"],
        "score": best["score"],
        "candidates": scored
    }

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is preventing Math-Boost?"
    result = route_query(q, {})
    print(json.dumps(result, indent=2))
