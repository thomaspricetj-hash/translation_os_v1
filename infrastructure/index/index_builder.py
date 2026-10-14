"""
Index Layer V0 Builder
Builds index_v0.json from all Translation OS sources
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = BASE_DIR / "infrastructure" / "index" / "index_v0.json"

def build_index():
    BASE = BASE_DIR
    sources = {
        "dictionary": BASE / "infrastructure" / "dictionary" / "dictionary_v0.json",
        "encyclopedia": BASE / "infrastructure" / "encyclopedia" / "encyclopedia_v0.json",
        "response_cache": BASE / "infrastructure" / "cache" / "response_cache_v0.json",
        "memory_reuse": BASE / "infrastructure" / "memory_reuse" / "memory_reuse_v0.json",
        "relevance_weights": BASE / "infrastructure" / "relevance" / "relevance_weights.json",
        "relevance_graph": BASE / "infrastructure" / "relevance" / "relevance_graph.json",
        "relevance_heatmap": BASE / "infrastructure" / "relevance" / "relevance_heatmap.json",
        "relevance_overlay": BASE / "infrastructure" / "relevance" / "relevance_overlay.json",
        "relevance_report": BASE / "infrastructure" / "relevance" / "relevance_report.json",
        "pattern_recognizer": BASE / "infrastructure" / "pattern_recognizer" / "patterns.json",
        "pattern_report": BASE / "infrastructure" / "pattern_recognizer" / "pattern_report.json",
        "picture_index": BASE / "infrastructure" / "picture_memory" / "picture_index.json",
        "debate_templates": BASE / "infrastructure" / "debate" / "debate_templates.json",
        "debate_history": BASE / "infrastructure" / "debate" / "debate_history.json",
        "debate_report": BASE / "infrastructure" / "debate" / "debate_layer_report.json",
        "problem_solve_templates": BASE / "infrastructure" / "problem_solve" / "problem_solve_templates.json",
        "problem_solve_report": BASE / "infrastructure" / "problem_solve" / "problem_solve_report.json",
        "knowledge_grid": BASE / "infrastructure" / "knowledge_grid" / "knowledge_grid_v0.json",
        "knowledge_grid_report": BASE / "infrastructure" / "knowledge_grid" / "knowledge_grid_report.json",
        "weave_layer": BASE / "infrastructure" / "weave" / "weave_layer_v0.json",
        "weave_report": BASE / "infrastructure" / "weave" / "weave_report.json",
        "policy": BASE / "infrastructure" / "policy" / "policy_v0.json",
        "policy_report": BASE / "infrastructure" / "policy" / "policy_report.json",
        "memory_weights": BASE / "infrastructure" / "memory_weights" / "memory_weights_v0.json",
        "memory_weight_report": BASE / "infrastructure" / "memory_weights" / "memory_weight_report.json",
        "reasoning_scoreboard": BASE / "infrastructure" / "reasoning_scoreboard" / "reasoning_scoreboard.json",
        "reasoning_scoreboard_report": BASE / "infrastructure" / "reasoning_scoreboard" / "reasoning_scoreboard_report.json",
        "reasoning_weights": BASE / "infrastructure" / "reasoning_weights" / "reasoning_weights.json",
        "reasoning_weight_report": BASE / "infrastructure" / "reasoning_weights" / "reasoning_weight_report.json",
        "diary": BASE / "workspace_memory" / "diary.json",
        "journal": BASE / "workspace_memory" / "journal.json",
        "project_book": BASE / "workspace_memory" / "project_book.json",
        "project_graph": BASE / "project_graph" / "project_graph_v0.json",
        "scoreboard": BASE / "scoreboard" / "capability_scoreboard.json",
    }
    entries = {}
    for name, path in sources.items():
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                # Create simple index entry pointing to file
                entries[name] = {
                    "file": str(path.relative_to(BASE_DIR)),
                    "indexed": True,
                    "entries_count": len(data) if isinstance(data, list) else 1
                }
            except Exception:
                entries[name] = {"file": str(path.relative_to(BASE_DIR)), "indexed": False}
        else:
            entries[name] = {"file": str(path.relative_to(BASE_DIR)), "indexed": False}
    
    index = {
        "metadata": {
            "version": "0.0",
            "built": "2026-10-13",
            "sources": list(sources.keys())
        },
        "entries": entries
    }
    return index

if __name__ == "__main__":
    idx = build_index()
    with open(INDEX_PATH, "w") as f:
        json.dump(idx, f, indent=2)
    print("Index V0 built")
