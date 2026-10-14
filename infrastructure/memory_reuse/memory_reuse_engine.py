"""
Memory Reuse V0 Engine
Reuse previous solutions, plans, and work products
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MEMORY_PATH = BASE_DIR / "memory_reuse_v0.json"
TEMPLATES_PATH = BASE_DIR / "reasoning_templates_v0.json"

with open(MEMORY_PATH) as f:
    MEMORY = json.load(f)

with open(TEMPLATES_PATH) as f:
    TEMPLATES = json.load(f)

def canonicalize(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def find_memory(query):
    q = canonicalize(query)
    for entry in MEMORY:
        sig = canonicalize(entry.get("query_signature",""))
        if sig and sig in q:
            return entry
    # fuzzy match on title
    for entry in MEMORY:
        title = canonicalize(entry.get("title",""))
        if title and title in q:
            return entry
    return None

def find_template(query):
    # simple heuristic based on keywords
    q = canonicalize(query)
    for t in TEMPLATES:
        typ = t["type"].lower()
        if typ.split()[0] in q:
            return t
    return None

def reuse_lookup(text):
    mem = find_memory(text)
    if mem:
        return {
            "source": "memory_reuse",
            "type": mem["type"],
            "title": mem["title"],
            "solution": mem["solution"],
            "status": mem["status"]
        }
    tmpl = find_template(text)
    if tmpl:
        return {
            "source": "reasoning_template",
            "type": tmpl["type"],
            "template": tmpl["template"]
        }
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python memory_reuse_engine.py 'query'")
        sys.exit(1)
    q = " ".join(sys.argv[1:])
    res = reuse_lookup(q)
    print(json.dumps(res, indent=2))
