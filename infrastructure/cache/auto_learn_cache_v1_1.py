"""
Response Cache v1.1 Auto-Learn
Promotes deterministic answers from Learning History to Response Cache
Safeguards:
- answer length < 50 words
- answer deterministic heuristic
- confidence high
- question appears multiple times
"""
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
HISTORY_PATH = BASE_DIR / "infrastructure" / "learning_loop" / "learning_history.json"
CACHE_PATH = BASE_DIR / "infrastructure" / "cache" / "response_cache_v0.json"
REPORT_PATH = BASE_DIR / "reports" / "response_cache_v1_1_report.json"

def load_json(p):
    try:
        with open(p) as f:
            return json.load(f)
    except:
        return {}

def save_json(p, data):
    with open(p, "w") as f:
        json.dump(data, f, indent=2)

def is_deterministic(answer):
    # Simple heuristic: short, no creative markers
    t = answer.lower()
    banned = ["maybe","perhaps","could","might","consider","write a story","analyze"]
    if any(b in t for b in banned):
        return False
    return True

def promote():
    history = load_json(HISTORY_PATH)
    entries = history.get("entries", [])
    # Group by normalized query
    groups = defaultdict(list)
    for e in entries:
        q = e.get("problem","").strip().lower()
        if not q:
            continue
        groups[q].append(e)
    
    cache = load_json(CACHE_PATH)
    new_entries = 0
    for q, items in groups.items():
        if len(items) < 2:
            continue
        # average success
        avg_success = sum(i.get("success_score",0) for i in items) / len(items)
        if avg_success < 0.85:
            continue
        # get most common answer
        answers = [i.get("answer","") for i in items]
        from collections import Counter
        common_answer, cnt = Counter(answers).most_common(1)[0]
        if len(common_answer.split()) > 50:
            continue
        if not is_deterministic(common_answer):
            continue
        # check if already cached
        already = False
        for eid, ent in cache.items():
            for pat in ent.get("patterns", []):
                if pat.lower() == q:
                    already = True
                    break
        if already:
            continue
        # create new entry
        qid = "AUTO_" + str(abs(hash(q)) % 100000)
        cache[qid] = {
            "question_id": qid,
            "patterns": [q],
            "answer": common_answer,
            "auto_learned": True,
            "hits": len(items),
            "avg_success": round(avg_success,3)
        }
        new_entries += 1
    
    save_json(CACHE_PATH, cache)
    
    report = {
        "auto_learned_entries": new_entries,
        "total_groups_evaluated": len(groups),
        "cache_size": len(cache),
        "safeguards": {
            "min_hits": 2,
            "min_success": 0.85,
            "max_words": 50,
            "deterministic_check": True
        }
    }
    save_json(REPORT_PATH, report)
    print(f"Auto-learn complete: {new_entries} entries promoted")
    return report

if __name__ == "__main__":
    promote()
