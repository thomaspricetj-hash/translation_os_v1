"""
Roundabout Router Micro Helper
Fast route scoring micro-helper
"""
def micro_score(route, query):
    q = query.lower()
    base = 0.5
    if route == "Response Cache" and "what is" in q:
        return 0.95
    if route == "Memory Reuse" and ("preventing" in q or "blocked" in q):
        return 0.98
    if route == "Math Route" and any(k in q for k in ["+", "-", "*", "/", "modulo"]):
        return 0.95
    return base
