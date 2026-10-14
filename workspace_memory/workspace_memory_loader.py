"""
Workspace Memory V1 Loader
Load order: Project Book -> Journal -> Diary -> Scratchpad
"""
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
PROJECT_BOOK = BASE_DIR / "project_book.json"
JOURNAL = BASE_DIR / "journal.json"
DIARY = BASE_DIR / "diary.json"
SCRATCHPAD = BASE_DIR / "scratchpad.json"

def load_project_book():
    with open(PROJECT_BOOK) as f:
        return json.load(f)

def load_recent_journal(limit=50):
    with open(JOURNAL) as f:
        entries = json.load(f)
    return entries[-limit:]

def load_diary():
    with open(DIARY) as f:
        return json.load(f)

def init_scratchpad(task_id=None):
    data = {
        "active_objectives": [],
        "extracted_facts": [],
        "pending_actions": [],
        "temporary_calculations": [],
        "task_id": task_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    with open(SCRATCHPAD, "w") as f:
        json.dump(data, f, indent=2)
    return data

def log_journal(action):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action
    }
    with open(JOURNAL) as f:
        entries = json.load(f)
    entries.append(entry)
    with open(JOURNAL, "w") as f:
        json.dump(entries, f, indent=2)

def append_diary(date, entry):
    with open(DIARY) as f:
        data = json.load(f)
    # find or create date entry
    for d in data:
        if d.get("date") == date:
            d.setdefault("entries", []).append(entry)
            break
    else:
        data.append({"date": date, "entries": [entry]})
    with open(DIARY, "w") as f:
        json.dump(data, f, indent=2)

def load_workspace(task_id=None):
    project = load_project_book()
    journal = load_recent_journal()
    diary = load_diary()
    scratchpad = init_scratchpad(task_id)
    return {
        "project_book": project,
        "journal": journal,
        "diary": diary,
        "scratchpad": scratchpad
    }

if __name__ == "__main__":
    ws = load_workspace(task_id="demo")
    print(json.dumps({
        "project": ws["project_book"].get("project"),
        "infrastructure": ws["project_book"].get("infrastructure"),
        "scratchpad_initialized": True
    }, indent=2))
