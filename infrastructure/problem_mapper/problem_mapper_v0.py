"""
Problem Mapper V0
Break complex problems into structured chunks before inference.
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PATTERNS_PATH = BASE_DIR / "problem_patterns_v0.json"

with open(PATTERNS_PATH) as f:
    PATTERNS = json.load(f)

def classify_category(text):
    t = text.lower()
    for p in PATTERNS:
        for pat in p.get("patterns", []):
            if re.search(pat, t):
                return p["category"]
    return "general"

def extract_facts(text, category):
    facts = []
    for p in PATTERNS:
        if p["category"] != category:
            continue
        for ext in p.get("extractors", []):
            for m in re.finditer(ext["regex"], text, re.IGNORECASE):
                facts.append({"type": ext["type"], "value": m.group(0)})
    # fallback: extract numbers
    nums = re.findall(r'\d+', text)
    for n in nums:
        if not any(n in f["value"] for f in facts):
            facts.append({"type": "number", "value": n})
    return facts

def map_problem(text):
    category = classify_category(text)
    facts = extract_facts(text, category)
    steps = []
    for p in PATTERNS:
        if p["category"] == category:
            steps = p.get("steps_template", [])
            break
    return {
        "type": category,
        "facts": facts,
        "steps": steps,
        "original": text
    }

def format_for_model(mapped):
    parts = [f"Problem type: {mapped['type']}"]
    if mapped["facts"]:
        parts.append("Facts:")
        for f in mapped["facts"]:
            parts.append(f"- {f['type']}: {f['value']}")
    if mapped["steps"]:
        parts.append("Suggested steps:")
        for s in mapped["steps"]:
            parts.append(f"- {s}")
    parts.append(f"\nOriginal question: {mapped['original']}")
    return "\n".join(parts)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python problem_mapper_v0.py 'your problem here'")
        sys.exit(1)
    text = " ".join(sys.argv[1:])
    mapped = map_problem(text)
    print(json.dumps(mapped, indent=2))
    print("\n--- Formatted for Model ---\n")
    print(format_for_model(mapped))
