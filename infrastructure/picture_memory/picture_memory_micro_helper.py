"""
Picture Memory Micro Helper V0
Micro utilities for fast picture memory access
"""
def quick_match(query, metadata):
    q = query.lower()
    for v in metadata.values():
        if isinstance(v, str) and q in v.lower():
            return True
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str) and q in item.lower():
                    return True
    return False
