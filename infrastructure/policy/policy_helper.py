"""
Policy Helper V0
Helper utilities for Policy Layer
"""
def get_policy_priorities():
    return ["cache_before_model", "reuse_before_rebuild", "resolve_blockers_before_new_work", "measure_before_keep", "project_continuity_first"]

def should_apply_policy(query):
    q = query.lower()
    return "what should" in q or "next" in q or "prevent" in q or "block" in q
