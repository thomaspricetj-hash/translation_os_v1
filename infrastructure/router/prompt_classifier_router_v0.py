"""
Prompt Classifier Router v0
Rule-based routing using HSCL-compressed text
Pipeline: Raw Text -> HSCL v1 -> Router v0 -> Muse-Glimmer
"""
import json
import re
from pathlib import Path

DICT_PATH = Path("hscl_dictionary_v1.json")
BENCH_PATH = Path("hscl_benchmark.json")

# Load HSCL dictionary and build patterns
with open(DICT_PATH) as f:
    dict_map = json.load(f)

def build_patterns(mapping):
    patterns = []
    for long_phrase, short in mapping.items():
        patterns.append((re.compile(r'\b'+re.escape(long_phrase)+r'\b', re.IGNORECASE), long_phrase, short))
    patterns.sort(key=lambda x: len(x[1]), reverse=True)
    return patterns

PATTERNS = build_patterns(dict_map)

def hscl_compress(text):
    res = text
    for pat, long_phrase, short in PATTERNS:
        def repl(m):
            mt = m.group(0)
            if mt.isupper():
                return short.upper()
            elif mt[0].isupper():
                return short.capitalize()
            else:
                return short
        res = pat.sub(repl, res)
    return res

# Rule-based classifier
MATH_INDICATORS = ["times", "divided", "percent of", "compute", "multiply", "learning rate"]
CODING_INDICATORS = ["python", "write code", "implement", "function", "bug", "error", "script", "algorithm", "convolutional neural network", "feed forward network", "recurrent neural network", "backpropagation", "stochastic gradient descent"]
REASONING_INDICATORS = ["compare", "analyze", "explain", "why", "how does", "difference between", "summarize", "role of", "describe the process", "works with", "gradient descent"]
CONVERSATION_INDICATORS = ["hello", "hi", "thanks", "opinion", "tell me about", "what is a", "explain ... in simple terms", "how does ... differ"]

def classify(text):
    t = text.lower()
    t_comp = hscl_compress(text).lower()
    combined = t + " " + t_comp
    
    # Priority order: Coding > Math > Reasoning > Conversation > General
    if any(ind in combined for ind in CODING_INDICATORS):
        return "Coding"
    
    has_digits = bool(re.search(r'\d', t))
    if has_digits and any(k in combined for k in ['times','divided','percent','compute','multiply','+','-','*','/','%']):
        return "Math"
    
    if any(ind in combined for ind in MATH_INDICATORS):
        return "Math"
    
    # Conversation specific overrides before general reasoning
    if 'in simple terms' in t or 'what is a ' in t or 'tell me about' in t:
        return "Conversation"
    if 'how does' in t and 'differ' in t:
        return "Conversation"
    
    if any(ind in combined for ind in REASONING_INDICATORS):
        return "Reasoning"
    
    if any(ind in combined for ind in CONVERSATION_INDICATORS):
        return "Conversation"
    
    return "General"

if __name__ == "__main__":
    with open(BENCH_PATH) as f:
        bench = json.load(f)
    
    results = []
    for category, prompts in bench["test_sets"].items():
        for p in prompts:
            pred = classify(p)
            results.append({
                "category": category,
                "prompt": p,
                "predicted": pred,
                "correct": pred.lower() == category.lower()
            })
    
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / len(results) if results else 0
    print(f"Routing accuracy: {accuracy:.2%} ({correct}/{len(results)})")
    print(json.dumps(results, indent=2))
