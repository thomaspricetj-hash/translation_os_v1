"""
Reasoning Weight Micro Helper V0
Fast micro-decisions for Adaptive Reasoning Weights
"""
def is_simple_query(query):
    q = query.lower()
    return any(k in q for k in ["2+2", "what is 2", "define ", "what is "]) and len(q.split()) < 10

def is_complex_planning_query(query):
    q = query.lower()
    return "plan" in q or "design" in q or "how should" in q or "comprehensive" in q

def estimate_query_complexity(query):
    q = query.lower()
    if is_simple_query(query):
        return "simple"
    if is_complex_planning_query(query):
        return "complex"
    return "medium"
