"""
Future Book V0 Queries
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FUTURE_BOOK_PATH = BASE_DIR / "workspace_memory" / "future_book.json"

def load_future_book():
    with open(FUTURE_BOOK_PATH) as f:
        return json.load(f)

def what_should_be_built_next():
    fb = load_future_book()
    return fb.get("current_goal")

def what_goals_are_blocked():
    fb = load_future_book()
    return fb.get("blocked_goals", [])

def what_depends_on(goal):
    fb = load_future_book()
    deps = []
    for bg in fb.get("blocked_goals", []):
        if goal in bg.get("blocked_by", []):
            deps.append(bg.get("goal"))
    return deps

def get_roadmap():
    fb = load_future_book()
    return fb.get("roadmap", [])

if __name__ == "__main__":
    fb = load_future_book()
    print("Next:", what_should_be_built_next())
    print("Blocked:", what_goals_are_blocked())
    print("Roadmap:", get_roadmap())
