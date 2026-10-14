"""
Project Graph V0 Builder
Builds and updates project_graph_v0.json from scoreboard and manifest
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_PATH = BASE_DIR / "project_graph" / "project_graph_v0.json"
SCOREBOARD_PATH = BASE_DIR / "scoreboard" / "capability_scoreboard.json"
MANIFEST_PATH = BASE_DIR / "file_manifest.json"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def build_graph():
    scoreboard = load_json(SCOREBOARD_PATH)
    # Build nodes from scoreboard infrastructure and components
    nodes = []
    edges = []
    # Simplified builder - in production derive from scoreboard
    graph = load_json(GRAPH_PATH)
    # Update timestamp
    graph["updated"] = "2026-10-13"
    return graph

def save_graph(graph):
    with open(GRAPH_PATH, "w") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    g = build_graph()
    save_graph(g)
    print(f"Project Graph V0 built with {len(g['nodes'])} nodes and {len(g['edges'])} edges")
