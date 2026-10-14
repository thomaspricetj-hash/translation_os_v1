"""
BD3D Hybrid Compression Helper
"""
from .bd3d_hybrid_v0 import BD3DHelper, BD3DMicroHelper

def should_compress_response(entry):
    helper = BD3DHelper()
    return helper.should_compress(len(str(entry)), "response")

def should_compress_workspace(record_type):
    helper = BD3DHelper()
    return helper.get_compression_priority(record_type) > 0.6
