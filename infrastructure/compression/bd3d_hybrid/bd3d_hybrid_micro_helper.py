"""
BD3D Hybrid Micro Helper
"""
from .bd3d_hybrid_v0 import BD3DMicroHelper

micro = BD3DMicroHelper()

def choose_backend(chunk_size):
    return micro.choose_backend(chunk_size)

def apply_skimming(data: bytes):
    return micro.apply_skimming(data)
