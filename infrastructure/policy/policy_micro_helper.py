"""
Policy Micro Helper V0
Fast micro-decisions for Policy Layer
"""
def is_planning_query(query):
    q = query.lower()
    return "what should i build" in q or "what should happen next" in q or "next step" in q

def is_blocker_query(query):
    q = query.lower()
    return "preventing" in q or "blocked" in q or "blocker" in q

def extract_policy_from_context(context):
    if "math-boost" in str(context).lower():
        return "resolve_blockers_before_new_work"
    return "cache_before_model"
