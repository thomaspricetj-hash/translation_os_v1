"""
Weave Micro Helper V0
Fast micro-decisions for Weave Layer
"""
def is_dependency_query(query):
    q = query.lower()
    return "what is preventing" in q or "blocked by" in q or "depends on" in q

def is_related_query(query):
    q = query.lower()
    return "related to" in q or "connected to" in q

def extract_node_from_query(query):
    # Simple heuristic: extract capitalized words or known nodes
    import re
    words = re.findall(r'[A-Z][a-zA-Z\-]+', query)
    return words[0] if words else None
