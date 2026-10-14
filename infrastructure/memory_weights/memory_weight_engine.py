"""
Memory Weight Engine V0
Determine what memory to keep, archive, or forget
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WEIGHTS_PATH = BASE_DIR / "infrastructure" / "memory_weights" / "memory_weights_v0.json"

def load_weights():
    with open(WEIGHTS_PATH) as f:
        return json.load(f)

def calculate_weight(memory_item):
    # Simple heuristic scoring 0-1
    # Normalize factors to 0-1
    score = 0.5
    # usage_frequency
    uf = memory_item.get("usage_frequency", "medium")
    uf_map = {"low": 0.2, "medium": 0.5, "high": 0.9}
    score += uf_map.get(uf, 0.5) * 0.2
    
    reuse = memory_item.get("reuse_count", 0)
    # Cap reuse impact
    reuse_score = min(reuse / 10.0, 1.0)
    score += reuse_score * 0.2
    
    pi = memory_item.get("project_importance", "medium")
    pi_map = {"low": 0.2, "medium": 0.5, "high": 0.9}
    score += pi_map.get(pi, 0.5) * 0.2
    
    # dependency_count
    deps = memory_item.get("dependency_count", 0)
    deps_score = min(deps / 5.0, 1.0)
    score += deps_score * 0.1
    
    # recency and success impact simplified
    recency = memory_item.get("recency", "medium")
    rec_map = {"old": 0.2, "medium": 0.5, "recent": 0.9}
    score += rec_map.get(recency, 0.5) * 0.1
    score += 0.1  # base
    
    # Normalize to 0-1
    weight = max(0.0, min(1.0, score / 1.5))
    return round(weight, 2)

def assign_tier(weight):
    if weight >= 0.90:
        return "core"
    elif weight >= 0.70:
        return "important"
    elif weight >= 0.50:
        return "standard"
    elif weight >= 0.20:
        return "archive"
    else:
        return "forgettable"

def process_memory(memory_item):
    weight = calculate_weight(memory_item)
    tier = assign_tier(weight)
    return {
        "item": memory_item,
        "weight": weight,
        "tier": tier
    }

if __name__ == "__main__":
    import sys
    sample = {
        "name": "HSCL v1",
        "usage_frequency": "high",
        "reuse_count": 50,
        "project_importance": "high",
        "dependency_count": 5,
        "recency": "recent"
    }
    print(json.dumps(process_memory(sample), indent=2))
