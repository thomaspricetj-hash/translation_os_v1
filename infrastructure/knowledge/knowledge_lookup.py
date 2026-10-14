"""
Knowledge Layer V0 Lookup
Dictionary + Encyclopedia lookup before model inference
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DICT_PATH = BASE_DIR / "knowledge_dictionary_v0.json"
ENC_PATH = BASE_DIR / "knowledge_encyclopedia_v0.json"

with open(DICT_PATH) as f:
    DICT = json.load(f)

with open(ENC_PATH) as f:
    ENC = json.load(f)

def canonicalize(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_term(text):
    t = text.lower().strip()
    prefixes = ["what is ", "define ", "explain ", "what does ", "who is "]
    for p in prefixes:
        if t.startswith(p):
            return canonicalize(t[len(p):].strip().strip('?'))
    return canonicalize(t)

def lookup_dictionary(term):
    for entry in DICT:
        word = canonicalize(entry["word"])
        if term == word:
            return entry["definition"]
        if term in [canonicalize(a) for a in entry.get("aliases", [])]:
            return entry["definition"]
        if term in [canonicalize(s) for s in entry.get("synonyms", [])]:
            return entry["definition"]
    return None

def lookup_encyclopedia(term):
    for entry in ENC:
        concept = canonicalize(entry["concept"])
        if term == concept:
            return entry["description"]
        if term in [canonicalize(r) for r in entry.get("related", [])]:
            return entry["description"]
    return None

def knowledge_lookup(text):
    term = extract_term(text)
    # Dictionary lookup
    d = lookup_dictionary(term)
    if d:
        return {"source": "knowledge_dictionary", "term": term, "response": d}
    # Encyclopedia lookup
    e = lookup_encyclopedia(term)
    if e:
        return {"source": "knowledge_encyclopedia", "term": term, "response": e}
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python knowledge_lookup.py 'query'")
        sys.exit(1)
    q = " ".join(sys.argv[1:])
    res = knowledge_lookup(q)
    print(json.dumps(res, indent=2))
