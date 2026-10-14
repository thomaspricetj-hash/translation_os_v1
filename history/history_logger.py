"""
History Book V0 Logger
Appends entries to history_book_v0.json
"""
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_PATH = BASE_DIR / "history" / "history_book_v0.json"

def log_history(event, event_type, result, reason):
    entry = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "event": event,
        "type": event_type,
        "result": result,
        "reason": reason
    }
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH) as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(HISTORY_PATH, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    log_history("Test entry", "test", "KEEP", "test reason")
    print("Logged")
