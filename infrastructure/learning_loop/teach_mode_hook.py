"""
Teach Mode Hook V0
Logs non-deterministic insights to Diary and Project Book for manual review
"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("TRANSLATION_OS_V1")
HISTORY = BASE / "infrastructure" / "learning_loop" / "learning_history.json"
DIARY = BASE / "workspace_memory" / "diary.json"
PROJECT_BOOK = BASE / "workspace_memory" / "project_book.json"

def load_json(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except:
        return {}

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_deterministic(answer):
    t = answer.lower()
    banned = ["maybe","perhaps","could","might","consider","write a story","analyze","design","compare"]
    return len(answer.split()) <= 50 and not any(b in t for b in banned)

def log_non_deterministic():
    hist = load_json(HISTORY)
    entries = hist.get("entries", [])
    diary = load_json(DIARY) or []
    project_book = load_json(PROJECT_BOOK) or {}

    new_notes = []
    for e in entries:
        ans = e.get("answer","")
        if not is_deterministic(ans):
            note = {
                "timestamp": e.get("timestamp", datetime.utcnow().isoformat()),
                "problem": e.get("problem",""),
                "answer_preview": ans[:300],
                "selected_layers": e.get("selected_layers",[]),
                "success_score": e.get("success_score",0),
                "note_type": "non_deterministic_insight"
            }
            new_notes.append(note)

    if new_notes:
        # Append to diary
        if isinstance(diary, list):
            diary.extend(new_notes)
        else:
            diary = {"entries": new_notes}
        save_json(DIARY, diary)

        # Update project book with teach mode stats
        project_book["teach_mode"] = {
            "last_run": datetime.utcnow().isoformat(),
            "non_deterministic_entries_logged": len(new_notes)
        }
        save_json(PROJECT_BOOK, project_book)

        print(f"Teach Mode: logged {len(new_notes)} non-deterministic insights to Diary")
    else:
        print("Teach Mode: no non-deterministic insights found")

if __name__ == "__main__":
    log_non_deterministic()
