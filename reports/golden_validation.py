"""
Golden Set Validation
Runs golden set through orchestrator and reports accuracy
"""
import json, subprocess, sys
from pathlib import Path

BASE = Path("TRANSLATION_OS_V1")
GOLDEN = BASE / "reports" / "golden_set.json"
OUT = BASE / "reports" / "golden_validation_report.json"

def run_query(q):
    out = subprocess.check_output([sys.executable, str(BASE / "orchestrator" / "master_orchestrator_v0.py"), q], text=True)
    return json.loads(out)

golden = json.load(open(GOLDEN))
results = []
for item in golden:
    res = run_query(item["query"])
    source = res.get("response_source")
    # simple check
    passed = False
    if item["type"] == "cache":
        passed = source == "cache"
    elif item["type"] == "picture":
        passed = res.get("picture_memory_hit") is True
    elif item["type"] == "reasoning":
        passed = res.get("model_called") is True
    results.append({
        "query": item["query"],
        "expected_type": item["type"],
        "source": source,
        "passed": passed
    })

report = {
    "total": len(results),
    "passed": sum(1 for r in results if r["passed"]),
    "results": results
}
json.dump(report, open(OUT, "w"), indent=2)
print(json.dumps(report, indent=2))
