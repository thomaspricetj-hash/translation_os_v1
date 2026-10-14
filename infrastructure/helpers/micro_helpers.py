"""
Micro helpers for fast decisions
"""
def is_definition(query):
    q = query.lower()
    return q.startswith("what is ") or q.startswith("define ")

def is_math(query):
    q = query.lower()
    return any(k in q for k in ["+", "-", "*", "/", "times", "divided", "percent", "calculate"])

def is_project(query):
    q = query.lower()
    return "translation os" in q or "project" in q
