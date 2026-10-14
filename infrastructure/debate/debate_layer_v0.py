"""
Debate Layer V0
Generate multiple solution approaches before selecting final answer
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_PATH = BASE_DIR / "infrastructure" / "debate" / "debate_templates.json"
HISTORY_PATH = BASE_DIR / "infrastructure" / "debate" / "debate_history.json"

def load_templates():
    with open(TEMPLATES_PATH) as f:
        return json.load(f)

def load_history():
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH) as f:
            return json.load(f)
    return {"history": []}

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

def debate(query, problem_type="planning"):
    templates = load_templates()
    tmpl = templates["templates"].get(problem_type, {"approaches": 3, "mode": "alternative_approaches"})
    mode = tmpl["mode"]
    approaches = tmpl["approaches"]
    
    # Simple heuristic generation
    approaches_list = []
    for i in range(approaches):
        approaches_list.append({
            "debater": f"Debater {chr(65+i)}",
            "approach": f"Approach {chr(65+i)} for {problem_type}",
            "pros": ["Benefit 1", "Benefit 2"],
            "cons": ["Cost 1", "Cost 2"]
        })
    
    judge = {
        "criteria": ["consistency", "completeness", "confidence", "dependency_awareness", "alignment"],
        "selected": approaches_list[0] if approaches_list else None,
        "reason": "Heuristic selection"
    }
    
    result = {
        "query": query,
        "problem_type": problem_type,
        "mode": mode,
        "approaches": approaches_list,
        "judge": judge
    }
    
    # Save to history
    hist = load_history()
    hist["history"].append(result)
    save_history(hist)
    
    return result

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How should Translation OS add GPU support?"
    print(json.dumps(debate(q, "gpu_support"), indent=2))
