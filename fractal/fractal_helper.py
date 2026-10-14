"""
Fractal Agent System Helper
Micro helper for task breakdown and agent assignment
"""
import json
from pathlib import Path

BASE = Path("TRANSLATION_OS_V1")
REGISTRY = BASE / "fractal" / "fractal_agent_registry.json"
TASK_QUEUE = BASE / "fractal" / "fractal_task_queue.json"

def get_agents_by_tags(tags):
    registry = json.load(open(REGISTRY))
    agents = []
    for ag in registry.get("agents", []):
        if any(t in ag.get("tags", []) for t in tags):
            agents.append(ag["agent_id"])
    return agents

def break_down_task(task_desc):
    # Simple heuristic breakdown
    tags = []
    desc_lower = task_desc.lower()
    if "plan" in desc_lower or "design" in desc_lower:
        tags.append("planning")
    if "code" in desc_lower or "implement" in desc_lower:
        tags.append("coding")
    if "test" in desc_lower or "benchmark" in desc_lower or "validate" in desc_lower:
        tags.append("validation")
    if "research" in desc_lower or "find" in desc_lower:
        tags.append("research")
    if "doc" in desc_lower or "write" in desc_lower:
        tags.append("documentation")
    if not tags:
        tags = ["planning", "coding", "validation"]
    return tags

if __name__ == "__main__":
    import sys
    desc = " ".join(sys.argv[1:])
    tags = break_down_task(desc)
    agents = get_agents_by_tags(tags)
    print(json.dumps({"task": desc, "tags": tags, "agents": agents}, indent=2))
