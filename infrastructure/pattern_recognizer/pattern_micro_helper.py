"""
Pattern Micro Helper
Fast pattern matching
"""
def quick_classify(query):
    q = query.lower()
    if "what is" in q and "pipeline" in q:
        return "Design"
    if "calculate" in q or "modulo" in q:
        return "Math"
    return "General"
