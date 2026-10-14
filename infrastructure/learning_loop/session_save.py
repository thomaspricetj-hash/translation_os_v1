"""
Session Save Hook V0
Ensures learning state persists after each session
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "infrastructure" / "learning_loop"))
from learning_loop_v0 import analyze_patterns, update_weights
sys.path.insert(0, str(BASE_DIR / "infrastructure" / "cache"))
from auto_learn_cache_v1_1 import promote

if __name__ == "__main__":
    print("Saving session state...")
    # Auto-learn cache from learning history
    auto_report = promote()
    print(f"Auto-learn promoted {auto_report.get('auto_learned_entries',0)} entries")
    # Teach mode: log non-deterministic insights
    try:
        from teach_mode_hook import log_non_deterministic
        log_non_deterministic()
    except Exception as e:
        print(f"Teach mode hook error: {e}")
    patterns = analyze_patterns()
    report = update_weights()
    print("Patterns updated:", len(patterns.get("patterns", [])))
    print("Learning state persisted to disk.")
    print("Files:")
    print(" - learning_history.json")
    print(" - learning_patterns.json")
    print(" - learning_loop_report.json")
    print(" - response_cache_v0.json updated")
    print(" - diary.json updated")
    print("Session save complete.")
