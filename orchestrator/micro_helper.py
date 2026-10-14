"""
Micro Helper V0
Fast micro-decisions for orchestrator
"""
def is_definition_query(query):
    q = query.lower()
    return q.startswith("what is ") or q.startswith("define ")

def is_math_query(query):
    q = query.lower()
    return any(k in q for k in ["+", "-", "*", "/", "times", "divided", "calculate"])

def is_project_query(query):
    q = query.lower()
    return "translation os" in q or "project" in q
