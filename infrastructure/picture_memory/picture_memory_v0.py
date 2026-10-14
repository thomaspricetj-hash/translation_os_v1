"""
Picture Memory V0
True picture memory where picture is the memory and lives in photo album
Picture is encoded with info about the picture
"""
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ALBUM_DIR = BASE_DIR / "infrastructure" / "picture_memory" / "photo_album"
INDEX_PATH = BASE_DIR / "infrastructure" / "picture_memory" / "picture_index.json"

def load_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"photos": []}

def save_index(idx):
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2)

def add_photo(photo_path, metadata):
    """
    Add a photo to album with encoded metadata
    metadata: dict with info about picture
    """
    if not photo_path.exists():
        raise FileNotFoundError(f"Photo not found: {photo_path}")
    # Copy to album
    ts = datetime.utcnow().isoformat().replace(":", "-")
    dest_name = f"{ts}_{photo_path.name}"
    dest_path = ALBUM_DIR / dest_name
    import shutil
    shutil.copy2(photo_path, dest_path)
    # Encode metadata into index
    idx = load_index()
    entry = {
        "filename": dest_name,
        "original_path": str(photo_path),
        "metadata": metadata,
        "encoded_at": datetime.utcnow().isoformat(),
        "memory_type": "picture_memory"
    }
    idx["photos"].append(entry)
    save_index(idx)
    return dest_path

def retrieve_photo_by_metadata(query):
    idx = load_index()
    results = []
    for photo in idx.get("photos", []):
        meta = photo.get("metadata", {})
        # Simple keyword match in metadata values
        for k,v in meta.items():
            if isinstance(v, str) and query.lower() in v.lower():
                results.append(photo)
                break
    return results

def get_photo_info(filename):
    idx = load_index()
    for photo in idx.get("photos", []):
        if photo["filename"] == filename:
            return photo
    return None

def main():
    print("Picture Memory V0 ready")
    print(f"Album: {ALBUM_DIR}")

if __name__ == "__main__":
    main()
