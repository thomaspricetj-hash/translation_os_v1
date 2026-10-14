"""
DAX KV-Delta Engine benchmark harness
Evaluates memory movement, rollback, branching vs naive KV cache
Run locally with PyTorch installed:
    python dax_kv_delta_benchmark.py
"""
import time
import torch
from dax_kv_delta_v0 import MasterKVCache, DeltaKVCache, DeltaKVEngine, SimpleAttention

def benchmark_reconstruction(seq_len=256, num_heads=8, head_dim=64, num_updates=100):
    B = 1
    D = num_heads * head_dim
    K_master = torch.randn(B, seq_len, num_heads, head_dim)
    V_master = torch.randn(B, seq_len, num_heads, head_dim)
    master = MasterKVCache(K_master, V_master)
    delta = DeltaKVCache()
    engine = DeltaKVEngine(master, delta)

    # Warmup
    for _ in range(10):
        engine.get_effective_kv()

    # Measure reconstruction cost with deltas
    for i in range(num_updates):
        pos = i % seq_len
        delta_K = torch.randn(num_heads, head_dim) * 0.01
        delta_V = torch.randn(num_heads, head_dim) * 0.01
        engine.add_token_delta(pos, delta_K, delta_V)

    t0 = time.perf_counter()
    for _ in range(100):
        K_eff, V_eff = engine.get_effective_kv()
    t_reconstruct = time.perf_counter() - t0

    # Rollback test
    t0 = time.perf_counter()
    engine.rollback_to(seq_len // 2)
    t_rollback = time.perf_counter() - t0

    # Branching cost test
    t0 = time.perf_counter()
    delta2 = DeltaKVCache()
    # copy existing entries for branch simulation
    delta2.entries = [e for e in delta.entries]
    t_branch = time.perf_counter() - t0

    # Memory usage estimate
    master_mem = K_master.numel() * 4 + V_master.numel() * 4  # bytes fp32
    delta_mem = sum(e[2].numel()*4 + e[3].numel()*4 for e in delta.entries)
    compression_ratio = master_mem / max(delta_mem,1)

    print("=== DAX KV-Delta Benchmark ===")
    print(f"Seq len: {seq_len}, Heads: {num_heads}, Head dim: {head_dim}")
    print(f"Reconstruction 100x: {t_reconstruct:.4f}s")
    print(f"Rollback to {seq_len//2}: {t_rollback*1000:.3f}ms")
    print(f"Branch copy: {t_branch*1000:.3f}ms")
    print(f"Master mem: {master_mem/1e6:.2f} MB")
    print(f"Delta mem: {delta_mem/1e6:.2f} MB")
    print(f"Compression ratio: {compression_ratio:.1f}x")
    print("=== End ===")

    return {
        "reconstruct_time": t_reconstruct,
        "rollback_ms": t_rollback*1000,
        "branch_ms": t_branch*1000,
        "compression_ratio": compression_ratio
    }

if __name__ == "__main__":
    benchmark_reconstruction()
