"""
Future Book V0 Planner
Manages future goals, dependencies, milestones, blockers
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FUTURE_BOOK_PATH = BASE_DIR / "workspace_memory" / "future_book.json"

def load_future_book():
    with open(FUTURE_BOOK_PATH) as f:
        return json.load(f)

def update_future_book(data):
    with open(FUTURE_BOOK_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_next_goal():
    fb = load_future_book()
    return fb.get("current_goal")

def get_blocked_goals():
    fb = load_future_book()
    return fb.get("blocked_goals", [])

def update_roadmap():
    fb = load_future_book()
    # Placeholder for automatic updates
    return fb.get("roadmap", [])

if __name__ == "__main__":
    fb = load_future_book()
    print(json.dumps(fb, indent=2))
