"""
Roundabout Router Golden Benchmark
"""
import json
from pathlib import Path
import sys

BASE = Path("TRANSLATION_OS_V1")
GOLDEN = BASE / "reports" / "golden_set.json"
HISTORY = BASE / "infrastructure" / "roundabout_router" / "route_history.json"

sys.path.insert(0, str(BASE / "infrastructure" / "roundabout_router"))
from roundabout_router_v0 import route_query

golden = json.load(open(GOLDEN))
results = []
for item in golden:
    q = item["query"]
    res = route_query(q, {})
    results.append({
        "query": q,
        "expected_type": item.get("type"),
        "selected_route": res["selected_route"],
        "score": res["score"]
    })

print(json.dumps(results, indent=2))
with open(BASE / "infrastructure" / "roundabout_router" / "roundabout_benchmark.json", "w") as f:
    json.dump(results, f, indent=2)
