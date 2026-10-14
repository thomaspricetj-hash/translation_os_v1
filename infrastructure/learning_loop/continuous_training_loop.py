"""
Continuous Training Loop
Iterates through subjects, teaches design, saves state
"""
import subprocess, sys
from pathlib import Path

BASE = Path("TRANSLATION_OS_V1")
TEACH_DIR = BASE / "infrastructure" / "learning_loop"
SESSION_SAVE = str(TEACH_DIR / "session_save.py")

subjects = [
    "design",
    "infrastructure",
    "history",
    "launcher",
    "orchestrator",
    "project_graph",
    "reports",
    "scoreboard",
    "workspace_memory",
]

print("Starting continuous training loop...")
for subj in subjects:
    script = TEACH_DIR / f"teach_{subj}.py"
    if script.exists():
        print(f"\n=== Teaching subject: {subj} ===")
        subprocess.run([sys.executable, str(script)], check=True)
        # Save state after each subject
        print("Saving session state...")
        subprocess.run([sys.executable, SESSION_SAVE], check=True)
    else:
        print(f"Skipping {subj}: script not found")

print("\nTraining loop complete. Design now knows everything taught.")
