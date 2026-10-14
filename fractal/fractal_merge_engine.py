"""
Fractal Merge Engine V0
Merges subtask results from agents into final solution
"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path("TRANSLATION_OS_V1")
TASK_QUEUE = BASE / "fractal" / "fractal_task_queue.json"
SCRATCHPAD = BASE / "fractal" / "fractal_shared_scratchpad.json"
REPORT = BASE / "fractal" / "fractal_report.json"
REGISTRY = BASE / "fractal" / "fractal_agent_registry.json"

def load_json(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except:
        return {}

def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def merge_task(task_id):
    queue = load_json(TASK_QUEUE)
    scratch = load_json(SCRATCHPAD)
    
    # Find task
    task = None
    for t in queue.get("tasks", []):
        if t.get("task_id") == task_id:
            task = t
            break
    
    if not task:
        return {"error": "task not found"}
    
    # Gather results from scratchpad sections
    sections = scratch.get("scratchpad", {})
    merged = {
        "task_id": task_id,
        "original_task": task.get("task", ""),
        "tags": task.get("tags", []),
        "subtask_results": {},
        "merged_solution": "",
        "conflicts": [],
        "merged_at": datetime.utcnow().isoformat()
    }
    
    for tag in task.get("tags", []):
        key = tag.upper()
        if key in sections:
            merged["subtask_results"][tag] = sections[key]
    
    # Conflict detection
    conflicts = []
    results_list = list(merged["subtask_results"].values())
    # Simple heuristic: if any result contains explicit conflict markers
    conflict_markers = ["conflict", "disagree", "contradict", "oppose"]
    for tag, res in merged["subtask_results"].items():
        low = res.lower()
        if any(m in low for m in conflict_markers):
            conflicts.append({"tag": tag, "reason": "conflict marker detected"})
    # Additional heuristic: planning vs coding mismatch on backend choice
    planning_res = merged["subtask_results"].get("planning", "").lower()
    coding_res = merged["subtask_results"].get("coding", "").lower()
    if "cuda only" in planning_res and "rocm" in coding_res:
        conflicts.append({"tag": "planning/coding", "reason": "backend mismatch"})
    merged["conflicts"] = conflicts
    
    # Simple merge: concatenate with separators
    parts = []
    for tag in task.get("tags", []):
        res = merged["subtask_results"].get(tag, "")
        if res:
            parts.append(f"[{tag.upper()}]\n{res}")
    
    merged["merged_solution"] = "\n\n---\n\n".join(parts)
    
    # Update task status
    for t in queue.get("tasks", []):
        if t.get("task_id") == task_id:
            t["status"] = "merged"
            t["merged_at"] = merged["merged_at"]
            break
    
    save_json(TASK_QUEUE, queue)
    
    # Update report
    report = load_json(REPORT)
    report.setdefault("merges", []).append(merged)
    report.setdefault("stats", {})["total_merges"] = report.get("stats", {}).get("total_merges", 0) + 1
    save_json(REPORT, report)
    
    # Auto-promote to workspace if no conflicts, else send to Debate Layer
    if not merged.get("conflicts"):
        try:
            import sys
            sys.path.insert(0, str(BASE / "workspace"))
            from workspace_manager import promote_to_workspace
            sandbox_file = BASE / "sandbox" / "agent_work" / "fractal_merge" / f"{task_id}_merged.md"
            sandbox_file.parent.mkdir(parents=True, exist_ok=True)
            with open(sandbox_file, "w", encoding="utf-8") as f:
                f.write(f"# Task ID: {task_id}\n# Original Task: {task.get('task','')}\n# Merged At: {merged['merged_at']}\n\n{merged['merged_solution']}")
            promote_to_workspace(str(sandbox_file.relative_to(BASE)), "tasks")
            merged["promoted_to_workspace"] = True
            merged["status"] = "promoted"
        except Exception as e:
            merged["promotion_error"] = str(e)
    else:
        # Conflict detected - send to Debate Layer, hold in sandbox
        try:
            debate_dir = BASE / "sandbox" / "agent_work" / "debate_queue"
            debate_dir.mkdir(parents=True, exist_ok=True)
            conflict_file = debate_dir / f"{task_id}_conflict.json"
            with open(conflict_file, "w", encoding="utf-8") as f:
                json.dump({
                    "task_id": task_id,
                    "original_task": task.get('task',''),
                    "conflicts": merged["conflicts"],
                    "subtask_results": merged["subtask_results"],
                    "merged_at": merged["merged_at"]
                }, f, indent=2)
            merged["status"] = "conflict_held_in_sandbox"
            merged["debate_queue_file"] = str(conflict_file.relative_to(BASE))
        except Exception as e:
            merged["debate_error"] = str(e)
    
    return merged

def create_task(task_desc, tags):
    queue = load_json(TASK_QUEUE)
    task_id = f"TASK_{len(queue.get('tasks', [])) + 1:04d}"
    task = {
        "task_id": task_id,
        "task": task_desc,
        "tags": tags,
        "status": "created",
        "created_at": datetime.utcnow().isoformat()
    }
    queue.setdefault("tasks", []).append(task)
    queue["metadata"]["total_tasks"] = len(queue["tasks"])
    queue["metadata"]["last_updated"] = datetime.utcnow().isoformat()
    save_json(TASK_QUEUE, queue)
    return task_id

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "create":
        desc = sys.argv[2]
        tags = sys.argv[3:]
        tid = create_task(desc, tags)
        print(f"Created task {tid}")
    elif len(sys.argv) > 2 and sys.argv[1] == "merge":
        tid = sys.argv[2]
        res = merge_task(tid)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: fractal_merge_engine.py create <desc> <tag1> <tag2> ...")
        print("       fractal_merge_engine.py merge <task_id>")
