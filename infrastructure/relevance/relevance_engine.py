"""
Weighted Relevance Engine V0
Determine what information/memory/knowledge/reasoning paths are most relevant to current problem
"""
import json
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent.parent

WEIGHTS_PATH = BASE_DIR / "infrastructure" / "relevance" / "relevance_weights.json"
GRAPH_PATH = BASE_DIR / "infrastructure" / "relevance" / "relevance_graph.json"
HEATMAP_PATH = BASE_DIR / "infrastructure" / "relevance" / "relevance_heatmap.json"
OVERLAY_PATH = BASE_DIR / "infrastructure" / "relevance" / "relevance_overlay.json"
REPORT_PATH = BASE_DIR / "infrastructure" / "relevance" / "relevance_report.json"

def load_json(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return json.load(f)
    except:
        return {}

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def keyword_similarity(query, text):
    q_words = set(re.findall(r'\w+', query.lower()))
    t_words = set(re.findall(r'\w+', text.lower()))
    if not q_words:
        return 0.0
    return len(q_words & t_words) / len(q_words)

def compute_relevance(query, component_name):
    # Placeholder heuristic
    # In real implementation, use keyword_similarity, concept_similarity, etc.
    # For now, simple mapping based on keywords
    q = query.lower()
    score = 0.5
    if "math" in q or "calculate" in q or "solve" in q:
        if component_name in ["Problem Mapper", "Problem Solve Layer", "Debate Layer"]:
            score = 0.95
        elif component_name == "Response Cache":
            score = 0.70
    elif "what is" in q or "define" in q:
        if component_name in ["Memory Reuse", "Encyclopedia"]:
            score = 0.90
        elif component_name == "Response Cache":
            score = 0.85
    else:
        score = 0.5
    return round(min(max(score, 0.0), 1.0), 3)

def score_component(query, comp_name, weights):
    comp_weights = weights.get("components", {}).get(comp_name, {})
    memory_w = comp_weights.get("memory_weight", 0.5)
    confidence_w = comp_weights.get("confidence_weight", 0.5)
    relevance_w = compute_relevance(query, comp_name)
    priority = round(memory_w * confidence_w * relevance_w, 3)
    decision = "ACTIVATE" if priority >= 0.5 else "SKIP"
    return {
        "component": comp_name,
        "memory_weight": memory_w,
        "confidence_weight": confidence_w,
        "relevance_weight": relevance_w,
        "priority_score": priority,
        "decision": decision
    }

def evaluate_query(query):
    weights = load_json(WEIGHTS_PATH)
    components = weights.get("components", {})
    results = []
    for comp_name in components.keys():
        results.append(score_component(query, comp_name, weights))
    # Sort by priority
    results.sort(key=lambda x: x["priority_score"], reverse=True)
    # Update heatmap
    heatmap = load_json(HEATMAP_PATH)
    heatmap.setdefault("heatmaps", []).append({
        "query": query,
        "scores": results,
        "timestamp": "2026-10-14T00:00:00Z"
    })
    save_json(HEATMAP_PATH, heatmap)
    return results

def main():
    query = "What is the pipeline order for Translation OS v1?"
    results = evaluate_query(query)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
