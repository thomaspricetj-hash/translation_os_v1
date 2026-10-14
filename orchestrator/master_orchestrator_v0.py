"""
Master Orchestrator V0
Ensures simple questions are answered by cheapest layer possible
Priority order:
1. Index
2. Dictionary
3. Encyclopedia
4. Response Cache
5. Memory Reuse
6. Memory Weight System
7. Knowledge Grid
8. Weave Layer
9. Policy Layer
10. Reasoning Weight Engine
11. Problem Mapper
12. Problem Solve Layer
13. Debate Layer
14. Reasoning Heatmap
15. Router
16. Muse-Glimmer
"""
import json
import re
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def canonicalize(text):
    t = text.lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def run_orchestrator(query):
    diagnostics = {
        "query": query,
        "index_hit": False,
        "dictionary_hit": False,
        "encyclopedia_hit": False,
        "cache_hit": False,
        "memory_reuse_hit": False,
        "picture_memory_hit": False,
        "knowledge_grid_hit": False,
        "problem_mapper_hit": False,
        "problem_solve_hit": False,
        "debate_hit": False,
        "reasoning_heatmap_hit": False,
        "router_hit": False,
        "model_called": False,
        "response_source": None,
        "response": None,
        "relevance_scores": None
    }
    q_canon = canonicalize(query)
    # Weighted Relevance Engine V0 integration
    try:
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "relevance"))
        from relevance_engine import evaluate_query
        relevance_results = evaluate_query(query)
        diagnostics["relevance_scores"] = relevance_results
    except Exception:
        diagnostics["relevance_scores"] = []
    # Pattern Recognizer V0 integration
    try:
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "pattern_recognizer"))
        from pattern_recognizer_v0 import recognize
        pattern_result = recognize(query, diagnostics)
        diagnostics["pattern_recognition"] = pattern_result
    except Exception:
        diagnostics["pattern_recognition"] = None
    
    # 2. Dictionary
    dict_path = BASE_DIR / "infrastructure" / "dictionary" / "dictionary_v0.json"
    dict_data = load_json(dict_path) or {}
    if q_canon.startswith("what is ") or q_canon.startswith("define "):
        query_term = q_canon.replace("what is ", "").replace("define ", "").strip()
        for k, v in dict_data.items():
            if canonicalize(k) == query_term:
                diagnostics["dictionary_hit"] = True
                diagnostics["response_source"] = "dictionary"
                diagnostics["response"] = v
                return diagnostics
    
    # 3. Encyclopedia
    enc_path = BASE_DIR / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json"
    enc_data = load_json(enc_path) or []
    if q_canon.startswith("what is ") or q_canon.startswith("define "):
        query_term = q_canon.replace("what is ", "").replace("define ", "").strip()
        for entry in enc_data:
            term = canonicalize(entry.get("term",""))
            aliases = [canonicalize(a) for a in entry.get("aliases",[])]
            if query_term == term or query_term in aliases:
                diagnostics["encyclopedia_hit"] = True
                diagnostics["response_source"] = "encyclopedia"
                diagnostics["response"] = entry.get("definition")
                return diagnostics
    
    # 4. Response Cache
    cache_path = BASE_DIR / "infrastructure" / "cache" / "response_cache_v0.json"
    cache_data = load_json(cache_path) or {}
    def cache_match(pat_canon, query_canon):
        # exact match or whole-word boundary match to avoid substring false positives
        if pat_canon == query_canon:
            return True
        # whole word boundary match
        import re
        pattern = r'\b' + re.escape(pat_canon) + r'\b'
        return re.search(pattern, query_canon) is not None
    for qid, entry in cache_data.items():
        patterns = entry.get("patterns",[])
        for pat in patterns:
            pat_canon = canonicalize(pat)
            if cache_match(pat_canon, q_canon):
                diagnostics["cache_hit"] = True
                diagnostics["response_source"] = "cache"
                diagnostics["response"] = entry.get("answer")
                return diagnostics
    
    # 5. Memory Reuse
    mem_path = BASE_DIR / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json"
    mem_data = load_json(mem_path) or []
    for entry in mem_data:
        sig = canonicalize(entry.get("query_signature",""))
        if sig and sig in q_canon:
            diagnostics["memory_reuse_hit"] = True
            diagnostics["response_source"] = "memory_reuse"
            diagnostics["response"] = entry.get("solution")
            return diagnostics

    # 5a. Picture Memory V0 - picture as memory, short-circuit before model
    try:
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "picture_memory"))
        from picture_memory_v0 import retrieve_photo_by_metadata, load_index
        pic_idx = load_index()
        # Simple metadata search using query canonicalized
        results = retrieve_photo_by_metadata(query)
        if results:
            diagnostics["picture_memory_hit"] = True
            # Return first match with metadata and file path
            photo = results[0]
            meta = photo.get("metadata", {})
            diagnostics["response_source"] = "picture_memory"
            diagnostics["response"] = {
                "filename": photo.get("filename"),
                "metadata": meta,
                "memory_type": photo.get("memory_type"),
                "encoded_at": photo.get("encoded_at")
            }
            return diagnostics
    except Exception:
        pass
    
    # 5b. Rule Engine
    if "design" in q_canon and ("translation os" in q_canon or "gpu support" in q_canon):
        diagnostics["response_source"] = "rule_engine"
        diagnostics["response"] = "Rule Engine: Project design request routed to Memory Reuse + Problem Mapper"
        return diagnostics
    
    # 5c. Roundabout Router V0 - evaluate multiple routes
    try:
        sys.path.insert(0, str(BASE_DIR / "infrastructure" / "roundabout_router"))
        from roundabout_router_v0 import route_query
        route_result = route_query(query, diagnostics)
        # If best route is not model and score > 0.8, follow it
        best_route = route_result.get("selected_route")
        best_score = route_result.get("score", 0)
        if best_score > 0.8 and best_route != "Muse-Glimmer":
            diagnostics["response_source"] = f"roundabout:{best_route}"
            diagnostics["roundabout_routes"] = route_result.get("candidates")
            diagnostics["response"] = f"Roundabout selected {best_route} with score {best_score}"
            return diagnostics
    except Exception:
        pass
    
    # 5d. Fractal Agent System V0 - auto-break large tasks
    try:
        # Detect large/complex tasks
        is_large = len(query) > 100 or query.count(".") >= 2 or " and " in q_canon
        if is_large:
            sys.path.insert(0, str(BASE_DIR / "fractal"))
            from fractal_helper import break_down_task
            tags = break_down_task(query)
            # Create fractal task
            sys.path.insert(0, str(BASE_DIR / "fractal"))
            import fractal_merge_engine as fe
            task_id = fe.create_task(query, tags)
            diagnostics["response_source"] = "fractal"
            diagnostics["response"] = {
                "task_id": task_id,
                "tags": tags,
                "message": "Task auto-broken into fractal subtasks",
                "next_step": "Agents will write to shared scratchpad, then merge"
            }
            return diagnostics
    except Exception as e:
        # Fail open to normal routing
        pass
    
    # 6. Problem Mapper
    math_keywords = ["+", "-", "*", "/", "times", "divided", "percent", "calculate"]
    coding_keywords = ["python", "code", "function", "implement", "bug", "error"]
    if any(k in q_canon for k in math_keywords):
        diagnostics["problem_mapper_hit"] = True
        diagnostics["response_source"] = "problem_mapper"
        diagnostics["response"] = "Problem mapped as math"
        return diagnostics
    if any(k in q_canon for k in coding_keywords):
        diagnostics["problem_mapper_hit"] = True
        diagnostics["response_source"] = "problem_mapper"
        diagnostics["response"] = "Problem mapped as coding"
        return diagnostics
    
    # 7. Router
    if any(k in q_canon for k in ["what is", "define", "explain"]):
        diagnostics["router_hit"] = True
        diagnostics["response_source"] = "router"
        diagnostics["response"] = "Routed to general"
        return diagnostics
    
    # 8. Muse-Glimmer
    diagnostics["model_called"] = True
    diagnostics["response_source"] = "model"
    diagnostics["response"] = "Model response placeholder"
    return diagnostics

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is 2+2?"
    print(json.dumps(run_orchestrator(q), indent=2))
