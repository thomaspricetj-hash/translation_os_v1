"""
Policy Engine V0
Defines how Translation OS chooses between actions
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
POLICY_PATH = BASE_DIR / "infrastructure" / "policy" / "policy_v0.json"

def load_policies():
    with open(POLICY_PATH) as f:
        return json.load(f)

def get_priorities():
    data = load_policies()
    return data.get("priorities", [])

def apply_policy(query, context):
    # Simple heuristic: if query mentions Math-Boost, apply resolve_blockers_before_new_work
    q = query.lower()
    policies = load_policies()
    active = []
    if "math-boost" in q or "prevent" in q or "blocking" in q:
        active.append("resolve_blockers_before_new_work")
    if "what is" in q or "define" in q:
        active.append("cache_before_model")
        active.append("reuse_before_rebuild")
    if "next" in q or "build" in q:
        active.append("resolve_blockers_before_new_work")
    return {
        "query": query,
        "active_policies": active,
        "priorities": get_priorities()
    }

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is preventing Math-Boost?"
    print(json.dumps(apply_policy(q, {}), indent=2))
