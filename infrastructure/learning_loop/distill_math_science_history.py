"""
Math Science History Knowledge Distillation
Teaches design everything about math, science, history from model
"""
import json, subprocess, sys
from pathlib import Path

BASE = Path("TRANSLATION_OS_V1")
LAUNCHER = str(BASE / "launcher" / "translation_os_v1.py")
CACHE_PATH = BASE / "infrastructure" / "cache" / "response_cache_v0.json"

TOPICS = [
    # Math
    "What is a prime number?",
    "What is the Pythagorean theorem?",
    "What is calculus?",
    "What is a derivative?",
    "What is an integral?",
    "What is the central limit theorem?",
    "What is the Riemann hypothesis?",
    "What is a matrix?",
    "What is linear algebra?",
    "What is a probability distribution?",
    # Science
    "What is the theory of relativity?",
    "What is quantum mechanics?",
    "What is the periodic table?",
    "What is photosynthesis?",
    "What is DNA?",
    "What is the Big Bang theory?",
    "What is Newton's laws of motion?",
    "What is thermodynamics?",
    "What is the scientific method?",
    "What is an atom?",
    # History
    "Who was Isaac Newton?",
    "Who was Albert Einstein?",
    "What was the Industrial Revolution?",
    "What was the Renaissance?",
    "What was World War II?",
    "Who was Marie Curie?",
    "What was the invention of the printing press?",
    "What was the American Revolution?",
    "What was the Cold War?",
    "Who was Leonardo da Vinci?",
]

def query_model(q):
    try:
        out = subprocess.check_output([sys.executable, LAUNCHER, q], text=True, timeout=120)
        data = json.loads(out)
        return data.get("response", "")
    except Exception as e:
        return f"[Error: {e}]"

cache = json.load(open(CACHE_PATH)) if CACHE_PATH.exists() else {}
new = 0
for q in TOPICS:
    ans = query_model(q)
    if len(ans.split()) > 150 or "[Model error" in ans:
        continue
    qid = "DISTILL_MS_" + str(abs(hash(q)) % 100000)
    cache[qid] = {
        "question_id": qid,
        "patterns": [q.lower()],
        "answer": ans[:800],
        "auto_learned": True,
        "source": "model_distill_math_science_history"
    }
    new += 1

json.dump(cache, open(CACHE_PATH, "w"), indent=2)
print(f"Distilled {new}/{len(TOPICS)} math science history topics into Response Cache")
