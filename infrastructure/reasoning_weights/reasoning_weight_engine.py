"""
Reasoning Weight Engine V0
Dynamically decide which reasoning layers are worth running
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WEIGHTS_PATH = BASE_DIR / "infrastructure" / "reasoning_weights" / "reasoning_weights.json"

def load_weights():
    with open(WEIGHTS_PATH) as f:
        return json.load(f)

def calculate_weight(layer):
    acc = layer.get("accuracy_delta", 0)
    reuse = layer.get("reuse_rate", 0)
    success = layer.get("success_rate", 0)
    latency = layer.get("latency_delta_ms", 1)
    # Normalize latency cost 0-1
    latency_cost = min(latency / 500.0, 1.0)
    weight = acc + reuse + success - latency_cost
    # Normalize to 0-1 range roughly
    weight = max(0.0, min(1.0, weight / 3.0))
    return round(weight, 2)

def assign_tier(weight):
    if weight >= 0.90:
        return "core"
    elif weight >= 0.70:
        return "important"
    elif weight >= 0.40:
        return "optional"
    else:
        return "low_value"

def select_layers(query_type="medium"):
    data = load_weights()
    layers = data.get("layers", [])
    results = []
    for layer in layers:
        w = calculate_weight(layer)
        tier = assign_tier(w)
        # Adaptive activation based on query type
        run = True
        if query_type == "simple" and tier in ["optional", "low_value"]:
            run = False
        if query_type == "definition" and layer["name"] in ["Problem Mapper", "Problem Solve Layer", "Debate Layer", "Reasoning Heatmap"]:
            run = False
        results.append({
            "name": layer["name"],
            "weight": w,
            "tier": tier,
            "run": run
        })
    return results

if __name__ == "__main__":
    import sys
    qtype = sys.argv[1] if len(sys.argv) > 1 else "medium"
    print(json.dumps(select_layers(qtype), indent=2))
