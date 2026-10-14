"""
Response Cache V0
Pipeline: Raw Text -> HSCL v1 -> Question Canonicalizer -> Response Cache -> Muse-Glimmer
"""
import json
import re
from pathlib import Path
import time

CACHE_PATH = Path("response_cache_v0.json")
DICT_PATH = Path("hscl_dictionary_v1.json")

# Load cache
with open(CACHE_PATH) as f:
    cache = json.load(f)

# Load HSCL patterns
with open(DICT_PATH) as f:
    dict_map = json.load(f)

def build_patterns(mapping):
    patterns = []
    for long_phrase, short in mapping.items():
        patterns.append((re.compile(r'\b'+re.escape(long_phrase)+r'\b', re.IGNORECASE), long_phrase, short))
    patterns.sort(key=lambda x: len(x[1]), reverse=True)
    return patterns

PATTERNS = build_patterns(dict_map)

def hscl_compress(text):
    res = text
    for pat, long_phrase, short in PATTERNS:
        def repl(m):
            mt = m.group(0)
            if mt.isupper():
                return short.upper()
            elif mt[0].isupper():
                return short.capitalize()
            else:
                return short
        res = pat.sub(repl, res)
    return res

def canonicalize(text):
    # Normalize: lowercase, remove punctuation, collapse whitespace
    t = hscl_compress(text).lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def find_cache_entry(query):
    canon = canonicalize(query)
    # Simple pattern matching
    for qid, entry in cache.items():
        for pat in entry['patterns']:
            if canonicalize(pat) == canon:
                return entry
    # Fuzzy: check if canon contains pattern or vice versa
    for qid, entry in cache.items():
        for pat in entry['patterns']:
            pc = canonicalize(pat)
            if pc in canon or canon in pc:
                return entry
    return None

def cache_lookup(query):
    entry = find_cache_entry(query)
    if entry:
        return True, entry['answer']
    return False, None

# Benchmark
TEST_QUERIES = [
    "What is 2+2?",
    "2+2",
    "calculate 2 plus 2",
    "What is the capital of France?",
    "what is an api",
    "Hello",
    "Explain quantum computing",  # miss
    "What is 17 times 23?",      # miss
]

hits = 0
latencies = []
for q in TEST_QUERIES:
    start = time.perf_counter()
    hit, ans = cache_lookup(q)
    lat = (time.perf_counter() - start) * 1000
    latencies.append(lat)
    if hit:
        hits += 1

hit_rate = hits / len(TEST_QUERIES)
avg_latency = sum(latencies)/len(latencies)

report = {
    "component": "Response Cache v0",
    "test_queries": len(TEST_QUERIES),
    "hits": hits,
    "hit_rate": hit_rate,
    "avg_lookup_latency_ms": avg_latency,
    "cache_entries": len(cache),
    "memory_cost_kb": Path(CACHE_PATH).stat().st_size / 1024,
    "status": "PENDING_REVIEW"
}

print(json.dumps(report, indent=2))
