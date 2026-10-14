"""
Learning Loop V0
Allow Translation OS to improve infrastructure based on solved problems
Do not modify Muse-Glimmer weights
"""
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
HISTORY_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_history.json"
PATTERNS_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_patterns.json"
REPORT_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_loop_report.json"
REASONING_SCOREBOARD_PATH = BASE_DIR / "infrastructure" / "reasoning_scoreboard" / "reasoning_scoreboard.json"

def load_json(p):
    try:
        with open(p) as f:
            return json.load(f)
    except:
        return {}

def save_json(p, data):
    with open(p, "w") as f:
        json.dump(data, f, indent=2)

def record_problem(problem, selected_layers, reasoning_path, answer, success_score, failure_score):
    history = load_json(HISTORY_PATH)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "problem": problem,
        "selected_layers": selected_layers,
        "reasoning_path": reasoning_path,
        "answer": answer,
        "success_score": success_score,
        "failure_score": failure_score
    }
    history.setdefault("entries", []).append(entry)
    save_json(HISTORY_PATH, history)
    return entry

def analyze_patterns():
    history = load_json(HISTORY_PATH)
    entries = history.get("entries", [])
    if not entries:
        return {"patterns": []}
    
    # Simple aggregation by problem type heuristic
    pattern_map = {}
    for e in entries:
        problem = e["problem"].lower()
        # heuristic classification
        if any(k in problem for k in ["+", "-", "*", "/", "times", "calculate", "modulo", "prime"]):
            ptype = "Math"
        elif "python" in problem or "code" in problem:
            ptype = "Coding"
        elif "arrang" in problem or "ways" in problem:
            ptype = "Combinatorics"
        else:
            ptype = "General"
        
        if ptype not in pattern_map:
            pattern_map[ptype] = {
                "count": 0,
                "router_correct": 0,
                "problem_mapper_helpful": 0,
                "debate_helpful": 0,
                "memory_reuse_helpful": 0,
                "cache_helpful": 0,
                "unnecessary_layers": 0,
                "success_sum": 0.0
            }
        stats = pattern_map[ptype]
        stats["count"] += 1
        stats["success_sum"] += e.get("success_score", 0)
        layers = e.get("selected_layers", [])
        # simple heuristics for layer helpfulness
        if "Router" in str(layers):
            stats["router_correct"] += 1
        if "Problem Mapper" in str(layers):
            stats["problem_mapper_helpful"] += 1
        if "Debate Layer" in str(layers):
            stats["debate_helpful"] += 1
        if "Memory Reuse" in str(layers):
            stats["memory_reuse_helpful"] += 1
        if "Cache" in str(layers):
            stats["cache_helpful"] += 1
    
    patterns = []
    for ptype, stats in pattern_map.items():
        count = stats["count"] or 1
        patterns.append({
            "problem_type": ptype,
            "samples": count,
            "avg_success": round(stats["success_sum"] / count, 3),
            "router_accuracy": round(stats["router_correct"] / count, 3),
            "problem_mapper_helpful_rate": round(stats["problem_mapper_helpful"] / count, 3),
            "debate_helpful_rate": round(stats["debate_helpful"] / count, 3),
            "memory_reuse_helpful_rate": round(stats["memory_reuse_helpful"] / count, 3),
            "cache_helpful_rate": round(stats["cache_helpful"] / count, 3),
            "recommendations": {
                "increase_weight": [],
                "decrease_weight": []
            }
        })
        # generate simple recommendations
        pm = patterns[-1]
        if pm["problem_mapper_helpful_rate"] >= 0.7:
            pm["recommendations"]["increase_weight"].append("Problem Mapper")
        if pm["debate_helpful_rate"] < 0.3:
            pm["recommendations"]["decrease_weight"].append("Debate Layer")
    
    patterns_data = load_json(PATTERNS_PATH)
    patterns_data["patterns"] = patterns
    patterns_data["last_updated"] = datetime.utcnow().isoformat()
    save_json(PATTERNS_PATH, patterns_data)
    return patterns_data

def update_weights():
    # Placeholder for Memory Weight System and Reasoning Weight updates
    # Read patterns, update weights files
    patterns = load_json(PATTERNS_PATH)
    report = load_json(REPORT_PATH)
    # Aggregate metrics
    metrics = {
        "routing_accuracy": None,
        "problem_mapping_accuracy": None,
        "reasoning_efficiency": None,
        "memory_reuse_rate": None,
        "layer_effectiveness": None
    }
    report["metrics"] = metrics
    report["last_update"] = datetime.utcnow().isoformat()
    report["status"] = "UPDATED"
    save_json(REPORT_PATH, report)
    return report

def main():
    # Example usage
    # record_problem(...)
    print("Learning Loop V0 initialized")
    print("History:", HISTORY_PATH)
    print("Patterns:", PATTERNS_PATH)
    print("Report:", REPORT_PATH)

if __name__ == "__main__":
    main()
