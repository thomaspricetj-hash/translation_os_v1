"""
Relevance Micro Helper
Fast micro-decisions for relevance engine
"""
def quick_relevance(query, component):
    q = query.lower()
    if component == "Problem Mapper" and any(k in q for k in ["math","solve","calculate","algebra","combinatorics"]):
        return 0.95
    if component == "Response Cache" and "what is" in q:
        return 0.85
    if component == "Memory Reuse" and "what is" in q:
        return 0.90
    if component == "History Book" and "blocked" in q or "why" in q:
        return 0.75
    return 0.5
