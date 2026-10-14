"""
Problem Solve Layer V0
Converts problem into explicit solution plan before model inference
"""
import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_PATH = BASE_DIR / "infrastructure" / "problem_solve" / "problem_solve_templates.json"

def load_templates():
    with open(TEMPLATES_PATH) as f:
        return json.load(f)

def solve_problem(query, problem_type):
    templates = load_templates()
    template = templates.get(problem_type, {})
    plan = {
        "problem_type": problem_type,
        "goal": template.get("goal_template", "Solve problem"),
        "steps": template.get("steps", []),
        "subgoals": template.get("subgoals", []),
        "dependencies": template.get("dependencies", []),
        "recommended_order": template.get("recommended_order", [])
    }
    return plan

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How do I add GPU support?"
    # Simple type detection
    ql = q.lower()
    if "gpu" in ql and "support" in ql:
        ptype = "gpu_support"
    elif any(k in ql for k in ["+", "-", "*", "/", "times", "calculate"]):
        ptype = "math"
    elif "python" in ql or "code" in ql:
        ptype = "coding"
    else:
        ptype = "planning"
    print(json.dumps(solve_problem(q, ptype), indent=2))
