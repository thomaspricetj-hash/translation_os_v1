"""
Reasoning Weight Helper V0
Helper utilities for Adaptive Reasoning Weights
"""
def get_reasoning_tiers():
    return {
        "core": [0.90, 1.00],
        "important": [0.70, 0.89],
        "optional": [0.40, 0.69],
        "low_value": [0.00, 0.39]
    }

def should_activate_layer(layer_name, query_type):
    # Simple heuristic
    if query_type == "simple" and layer_name in ["Debate Layer", "Reasoning Heatmap", "Weave Layer"]:
        return False
    if query_type == "definition" and layer_name in ["Problem Mapper", "Problem Solve Layer", "Debate Layer"]:
        return False
    return True
