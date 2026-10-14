"""
Sandbox + Workspace V0 Manager
Ensures fractal agents write to sandbox first, then promotion to workspace
"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("TRANSLATION_OS_V1")
WORKSPACE = BASE / "workspace"
SANDBOX = BASE / "sandbox"
ARCHIVE = BASE / "archive"
INDEX = WORKSPACE / "workspace_index.json"

def load_json(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except:
        return {}

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def write_agent_output(agent_id, tag, content):
    # Write to sandbox first
    agent_dir = SANDBOX / "agent_work" / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_path = agent_dir / f"{tag}_{timestamp}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Agent: {agent_id}\n# Tag: {tag}\n# Timestamp: {datetime.utcnow().isoformat()}\n\n{content}")
    
    # Update shared scratchpad
    scratchpad = BASE / "fractal" / "fractal_shared_scratchpad.json"
    data = load_json(scratchpad)
    if "scratchpad" not in data:
        data["scratchpad"] = {}
    # Append content
    existing = data["scratchpad"].get(tag.upper(), "")
    data["scratchpad"][tag.upper()] = (existing + "\n\n" + content).strip()
    save_json(scratchpad, data)
    
    # Update index
    idx = load_json(INDEX)
    idx.setdefault("index", {}).setdefault("agent_outputs", []).append({
        "agent_id": agent_id,
        "tag": tag,
        "file": str(file_path.relative_to(BASE)),
        "timestamp": datetime.utcnow().isoformat()
    })
    idx["last_updated"] = datetime.utcnow().isoformat()
    save_json(INDEX, idx)
    
    return str(file_path.relative_to(BASE))

def promote_to_workspace(file_rel_path, target_dir):
    src = BASE / file_rel_path
    dst_dir = WORKSPACE / target_dir
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    import shutil
    shutil.copy2(src, dst)
    return str(dst.relative_to(BASE))

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 3 and sys.argv[1] == "write":
        agent_id = sys.argv[2]
        tag = sys.argv[3]
        content = " ".join(sys.argv[4:])
        path = write_agent_output(agent_id, tag, content)
        print(f"Wrote to sandbox: {path}")
    elif len(sys.argv) > 3 and sys.argv[1] == "promote":
        rel_path = sys.argv[2]
        target = sys.argv[3]
        dst = promote_to_workspace(rel_path, target)
        print(f"Promoted to workspace: {dst}")
    else:
        print("Usage: workspace_manager.py write <agent_id> <tag> <content>")
        print("       workspace_manager.py promote <rel_path> <target_dir>")
