"""
Integration test for DAX KV-Delta Engine with Translation OS concepts
Tests correctness of effective KV reconstruction vs naive update
"""
import torch
from dax_kv_delta_v0 import MasterKVCache, DeltaKVCache, DeltaKVEngine

def test_correctness():
    B=1; L=16; H=4; D=16
    K_master = torch.randn(B,L,H,D)
    V_master = torch.randn(B,L,H,D)
    master = MasterKVCache(K_master, V_master)
    engine = DeltaKVEngine(master)

    # Apply known deltas
    pos=5
    delta_K = torch.randn(H,D)*0.1
    delta_V = torch.randn(H,D)*0.1
    engine.add_token_delta(pos, delta_K, delta_V)

    K_eff, V_eff = engine.get_effective_kv()
    # Manual expected
    K_expected = K_master.clone()
    V_expected = V_master.clone()
    K_expected[0,pos] += delta_K
    V_expected[0,pos] += delta_V

    k_ok = torch.allclose(K_eff, K_expected, atol=1e-6)
    v_ok = torch.allclose(V_eff, V_expected, atol=1e-6)
    print("KV reconstruction correct:", k_ok and v_ok)
    return k_ok and v_ok

def test_rollback():
    B=1; L=16; H=4; D=16
    K_master = torch.zeros(B,L,H,D)
    V_master = torch.zeros(B,L,H,D)
    engine = DeltaKVEngine(MasterKVCache(K_master, V_master))
    for p in range(10):
        engine.add_token_delta(p, torch.ones(H,D)*p, torch.ones(H,D)*p)
    engine.rollback_to(4)
    K_eff,_ = engine.get_effective_kv()
    # positions >4 should be zero
    ok = torch.allclose(K_eff[0,5:], torch.zeros_like(K_eff[0,5:]))
    print("Rollback correct:", ok)
    return ok

if __name__=="__main__":
    test_correctness()
    test_rollback()
