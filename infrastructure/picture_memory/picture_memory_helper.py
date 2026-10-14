"""
Picture Memory Helper V0
Helper utilities for picture memory operations
"""
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = BASE_DIR / "infrastructure" / "picture_memory" / "picture_index.json"

def get_all_photos():
    if INDEX_PATH.exists():
        with open(INDEX_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("photos", [])
    return []

def find_photos_by_tag(tag):
    photos = get_all_photos()
    matches = []
    for p in photos:
        meta = p.get("metadata", {})
        tags = meta.get("tags", [])
        if tag.lower() in [t.lower() for t in tags]:
            matches.append(p)
    return matches

def summarize_album():
    photos = get_all_photos()
    return {
        "total_photos": len(photos),
        "memory_type": "picture_memory",
        "indexed": True
    }
