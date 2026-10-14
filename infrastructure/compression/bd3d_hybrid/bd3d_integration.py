"""
BD3D Hybrid Compression Integration for Translation OS
Wires compression into Response Cache, Workspace Memory, Memory Reuse
"""
from .bd3d_hybrid_v0 import compress_response_cache, compress_workspace_memory, compress_memory_reuse

# Integration points
RESPONSE_CACHE_HOOK = "compress_response_cache"
WORKSPACE_MEMORY_HOOK = "compress_workspace_memory"
MEMORY_REUSE_HOOK = "compress_memory_reuse"

def apply_compression_to_response_cache(entry):
    return compress_response_cache(entry)

def apply_compression_to_workspace_memory(record):
    return compress_workspace_memory(record)

def apply_compression_to_memory_reuse(solution):
    return compress_memory_reuse(solution)

# Master Orchestrator hook registration
INTEGRATION_MAP = {
    "response_cache": apply_compression_to_response_cache,
    "workspace_memory": apply_compression_to_workspace_memory,
    "memory_reuse": apply_compression_to_memory_reuse
}
