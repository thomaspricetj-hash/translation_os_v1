"""
Pattern Helper
Utilities for pattern recognition
"""
import re

def extract_keywords(query):
    return set(re.findall(r'\w+', query.lower()))
