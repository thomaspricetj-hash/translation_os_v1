"""
Reasoning Heatmap V0
Track fact importance, knowledge sources, and reasoning steps
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_PATH = BASE_DIR / "reasoning_templates.json"
STORAGE_PATH = BASE_DIR / "heatmap_storage.json"

with open(TEMPLATES_PATH) as f:
    TEMPLATES = json.load(f)

with open(STORAGE_PATH) as f:
    STORAGE = json.load(f)

def get_template(problem_type):
    for t in TEMPLATES:
        if t["type"].lower() == problem_type.lower():
            return t
    return None

def log_heatmap(problem_id, query, fact_heatmap, knowledge_heatmap, reasoning_heatmap, answer, success):
    entry = {
        "problem_id": problem_id,
        "query": query,
        "fact_heatmap": fact_heatmap,
        "knowledge_heatmap": knowledge_heatmap,
        "reasoning_heatmap": reasoning_heatmap,
        "answer": answer,
        "success": success,
        "created": "2026-10-13"
    }
    STORAGE.append(entry)
    with open(STORAGE_PATH, "w") as f:
        json.dump(STORAGE, f, indent=2)

def reuse_heatmap(query):
    # simple signature match
    q = query.lower()
    for entry in STORAGE:
        if entry["query"].lower() in q or q in entry["query"].lower():
            return entry
    return None

def build_overlay(problem_type, facts, sources):
    template = get_template(problem_type)
    return {
        "problem_type": problem_type,
        "template": template["steps"] if template else [],
        "facts": facts,
        "sources": sources
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python reasoning_heatmap_v0.py 'query'")
        sys.exit(1)
    q = " ".join(sys.argv[1:])
    hit = reuse_heatmap(q)
    print(json.dumps(hit, indent=2))
