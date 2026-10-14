"""
Orchestrator Helper V0
Provides helper utilities for Master Orchestrator
"""
def get_layer_priority():
    return ["Index","Dictionary","Encyclopedia","Response Cache","Memory Reuse","Memory Weight System","Knowledge Grid","Weave Layer","Policy Layer","Reasoning Weight Engine","Rule Engine","Problem Mapper","Problem Solve Layer","Debate Layer","Reasoning Heatmap","Router","Muse-Glimmer"]

def should_short_circuit(response_source):
    return response_source is not None and response_source != "model"
