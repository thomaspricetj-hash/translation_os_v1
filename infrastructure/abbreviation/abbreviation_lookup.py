"""
Abbreviation Dictionary V0 Lookup
Normalizes abbreviations to canonical concepts
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DICT_PATH = BASE_DIR / "infrastructure" / "abbreviation" / "abbreviation_dictionary_v0.json"

def load_dict():
    with open(DICT_PATH) as f:
        return json.load(f)

def normalize(text):
    d = load_dict()
    # Replace abbreviations with canonical forms
    # Word boundary matching
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in d.keys()) + r')\b', re.IGNORECASE)
    def repl(m):
        key = m.group(0).upper()
        if key in d:
            return d[key]["canonical"]
        return m.group(0)
    return pattern.sub(repl, text)

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How does an AI use a GPU?"
    print(normalize(q))
