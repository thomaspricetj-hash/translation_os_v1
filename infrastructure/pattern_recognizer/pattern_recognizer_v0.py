"""
Pattern Recognizer V0
Detect recurring problem types, successful reasoning paths, layer activations
"""
import json
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PATTERNS_PATH = BASE_DIR / "infrastructure" / "pattern_recognizer" / "patterns.json"
REPORT_PATH = BASE_DIR / "infrastructure" / "pattern_recognizer" / "pattern_report.json"

def load_json(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except:
        return {}

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def classify_problem_type(query):
    q = query.lower()
    if any(k in q for k in ["math","calculate","solve","times","divide","modulo","prime"]):
        return "Math"
    if "python" in q or "code" in q or "function" in q:
        return "Coding"
    if "what is" in q or "define" in q or "explain" in q:
        return "Definition"
    if "pipeline" in q or "architecture" in q or "design" in q:
        return "Design"
    return "General"

def recognize(query, orchestrator_diagnostics):
    problem_type = classify_problem_type(query)
    patterns = load_json(PATTERNS_PATH)
    patterns.setdefault("problem_types", {})
    pt = patterns["problem_types"]
    pt.setdefault(problem_type, {"count":0, "successful_paths":[]})
    pt[problem_type]["count"] += 1
    
    # Detect successful path from diagnostics
    path_key = orchestrator_diagnostics.get("response_source")
    pt[problem_type].setdefault("successful_paths", []).append(path_key)
    
    save_json(PATTERNS_PATH, patterns)
    return {
        "problem_type": problem_type,
        "pattern_id": f"{problem_type}_{pt[problem_type]['count']}",
        "suggested_layers": suggest_layers(problem_type)
    }

def suggest_layers(problem_type):
    suggestions = {
        "Math": ["Problem Mapper","Problem Solve Layer","Debate Layer"],
        "Coding": ["Problem Mapper","Problem Solve Layer"],
        "Definition": ["Memory Reuse","Encyclopedia","Response Cache"],
        "Design": ["Memory Reuse","Encyclopedia","Project Graph"],
        "General": ["Memory Reuse","Response Cache"]
    }
    return suggestions.get(problem_type, ["Memory Reuse"])

def main():
    print("Pattern Recognizer V0 ready")

if __name__ == "__main__":
    main()
