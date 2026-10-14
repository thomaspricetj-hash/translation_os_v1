"""
Weave Query V0
Query cross-system relationships
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WEAVE_PATH = BASE_DIR / "infrastructure" / "weave" / "weave_layer_v0.json"

def load_weave():
    with open(WEAVE_PATH) as f:
        return json.load(f)

def find_related_systems(node, top_n=5):
    data = load_weave()
    links = data.get("links", [])
    related = []
    for l in links:
        if l["from"] == node or l["to"] == node:
            related.append(l)
    related.sort(key=lambda x: x["weight"], reverse=True)
    return related[:top_n]

def find_indirect_dependencies(start_node, depth=3):
    data = load_weave()
    links = data.get("links", [])
    visited = set()
    chain = []
    current = start_node
    for _ in range(depth):
        found = False
        for l in links:
            if l["from"] == current and l["to"] not in visited:
                visited.add(l["to"])
                chain.append(l)
                current = l["to"]
                found = True
                break
        if not found:
            break
    return chain

def show_strongest_connections(top_n=5):
    data = load_weave()
    links = data.get("links", [])
    links_sorted = sorted(links, key=lambda x: x["weight"], reverse=True)
    return links_sorted[:top_n]

if __name__ == "__main__":
    import sys
    node = sys.argv[1] if len(sys.argv) > 1 else "Math-Boost"
    print(json.dumps({
        "related": find_related_systems(node),
        "indirect_chain": find_indirect_dependencies(node),
        "strongest": show_strongest_connections()
    }, indent=2))
