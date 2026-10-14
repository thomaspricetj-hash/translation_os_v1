"""
HSCL V1 Preprocessor - Phrase Compression Only
Pipeline: Raw Text -> HSCL Compressor -> Compressed Text -> Tokenizer
"""
import json
import re
from pathlib import Path

DICT_PATH = Path("hscl_dictionary_v1.json")

with open(DICT_PATH, 'r', encoding='utf-8') as f:
    dict_map = json.load(f)

# Build mapping from long phrase to short abbreviation
# dict_map is currently long->short as per spec
# Ensure case-insensitive matching
def build_patterns(mapping):
    patterns = []
    for long_phrase, short in mapping.items():
        # Escape for regex, allow word boundaries
        pattern = re.compile(r'\b' + re.escape(long_phrase) + r'\b', flags=re.IGNORECASE)
        patterns.append((pattern, long_phrase, short))
    # Sort by length of long phrase descending for longest match first
    patterns.sort(key=lambda x: len(x[1]), reverse=True)
    return patterns

PATTERNS = build_patterns(dict_map)

def compress(text: str) -> str:
    # Only compress recognized phrases, leave unknown text untouched
    result = text
    for pattern, long_phrase, short in PATTERNS:
        # Replace whole word matches case-insensitively, preserving original case style
        def repl(m):
            match_text = m.group(0)
            # Preserve case: if original is upper, make short upper; if title, title case
            if match_text.isupper():
                return short.upper()
            elif match_text[0].isupper():
                return short.capitalize()
            else:
                return short
        result = pattern.sub(repl, result)
    return result

def decompress(text: str) -> str:
    # Reverse mapping for debugging
    rev_map = {v.lower(): k for k, v in dict_map.items()}
    # Simple replace - not used in pipeline
    return text

if __name__ == "__main__":
    examples = [
        "artificial intelligence and machine learning",
        "large language model for natural language processing",
        "New York City is in the United States of America",
        "deep learning and reinforcement learning",
        "unknown phrase should remain untouched"
    ]
    for ex in examples:
        comp = compress(ex)
        print(f"Input:  {ex}")
        print(f"Output: {comp}")
        print()
