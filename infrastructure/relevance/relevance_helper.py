"""
Relevance Helper
Utilities for relevance scoring
"""
import re

def normalize_text(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def keyword_overlap(a, b):
    a_set = set(re.findall(r'\w+', a.lower()))
    b_set = set(re.findall(r'\w+', b.lower()))
    if not a_set:
        return 0.0
    return len(a_set & b_set) / len(a_set)

def concept_similarity(query, component_desc):
    # Placeholder
    return keyword_overlap(query, component_desc)
