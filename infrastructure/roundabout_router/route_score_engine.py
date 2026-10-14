"""
Route Score Engine V0
Scores candidate routes based on confidence, relevance, reasoning, memory weights
"""
import json
from pathlib import Path

BASE = Path("TRANSLATION_OS_V1")

def score_route(route_name, query, diagnostics):
    # Base weights from relevance engine
    weights = {
        "Dictionary": 0.9,
        "Encyclopedia": 0.85,
        "Response Cache": 0.95,
        "Memory Reuse": 0.88,
        "Project Graph": 0.8,
        "Knowledge Grid": 0.75,
        "Problem Solve Layer": 0.85,
        "Debate Layer": 0.7,
        "Muse-Glimmer": 0.6
    }
    # Simple heuristic scoring
    q = query.lower()
    score = weights.get(route_name, 0.5)
    
    # Boost based on keywords
    if route_name == "Response Cache" and "what is" in q:
        score *= 1.1
    if route_name == "Memory Reuse" and ("preventing" in q or "blocked" in q):
        score *= 1.2
    if route_name == "Math Route" and any(k in q for k in ["+", "-", "*", "/", "catalan", "modulo"]):
        score *= 1.3
    if route_name == "Planning Route" and ("design" in q or "plan" in q):
        score *= 1.15
    # Reasoning boost for complex math/decimal queries
    if route_name in ["Problem Solve Layer", "Debate Layer", "Muse-Glimmer"] and any(k in q for k in ["find", "digit", "decimal", "expansion", "1000th"]):
        score *= 1.4
    # Picture route boost
    if route_name == "Response Cache" and "diagram" in q:
        score *= 0.7  # demote cache for picture
    # Reduce cache score for hard reasoning
    if route_name == "Response Cache" and ("find" in q and "digit" in q):
        score *= 0.5
    
    return min(1.0, score)

def evaluate_routes(query, diagnostics):
    routes = [
        "Dictionary", "Encyclopedia", "Response Cache", "Memory Reuse",
        "Project Graph", "Knowledge Grid", "Problem Solve Layer", "Debate Layer",
        "Muse-Glimmer"
    ]
    scored = []
    for r in routes:
        s = score_route(r, query, diagnostics)
        scored.append({"route": r, "score": round(s, 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
