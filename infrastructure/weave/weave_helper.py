"""
Weave Helper V0
Helper utilities for Weave Layer
"""
def get_weave_priority():
    return ["related_systems", "indirect_dependencies", "strongest_connections", "likely_next_actions", "recurring_patterns"]

def should_weave_query(query):
    q = query.lower()
    return "prevent" in q or "blocking" in q or "dependency" in q or "related" in q
