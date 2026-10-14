"""
Roundabout Router Helper
Micro helper for route candidate generation
"""
import json
from pathlib import Path

BASE = Path("TRANSLATION_OS_V1")

def generate_candidates(query):
    q = query.lower()
    candidates = []
    if "what is" in q or "define" in q:
        candidates.extend(["Dictionary", "Encyclopedia", "Response Cache"])
    if "preventing" in q or "blocked" in q:
        candidates.append("Memory Reuse")
    if any(k in q for k in ["+", "-", "*", "/", "modulo", "catalan"]):
        candidates.append("Math Route")
    if "design" in q or "plan" in q:
        candidates.append("Planning Route")
    if "code" in q or "implement" in q:
        candidates.append("Coding Route")
    if not candidates:
        candidates = ["Muse-Glimmer"]
    return list(dict.fromkeys(candidates))

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:])
    print(json.dumps({"candidates": generate_candidates(q)}, indent=2))
