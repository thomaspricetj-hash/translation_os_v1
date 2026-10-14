"""
General helpers for Translation OS
"""
def canonicalize(text):
    import re
    t = text.lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def load_json_safe(path):
    import json
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None
