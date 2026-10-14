import torch
from typing import List, Tuple, Optional


class MasterKVCache:
    """
    Master KV cache: base, shared context.
    Shape:
        K: [batch, seq_len, num_heads, head_dim]
        V: [batch, seq_len, num_heads, head_dim]
    """

    def __init__(self, K_master: torch.Tensor, V_master: torch.Tensor):
        assert K_master.shape == V_master.shape
        self.K_master = K_master  # [B, L, H, D]
        self.V_master = V_master  # [B, L, H, D]

    @property
    def device(self):
        return self.K_master.device

    @property
    def shape(self):
        return self.K_master.shape


class DeltaKVCache:
    """
    Delta KV cache: stores only changes relative to master.
    We keep a sparse list of (pos, head, delta_K, delta_V) per batch.
    For simplicity, we assume batch size 1 in this first implementation.
    You can extend to per-batch indexing if needed.
    """

    def __init__(self):
        # entries: List[(pos: int, head: int, delta_K: Tensor[D], delta_V: Tensor[D])]
        self.entries: List[Tuple[int, int, torch.Tensor, torch.Tensor]] = []

    def add_delta(self, pos: int, head: int,
                  delta_K: torch.Tensor,
                  delta_V: torch.Tensor):
        """
        pos: token index in sequence
        head: attention head index
        delta_K: [head_dim]
        delta_V: [head_dim]
        """
        assert delta_K.shape == delta_V.shape
        self.entries.append((pos, head, delta_K.detach(), delta_V.detach()))

    def clear_after(self, pos: int):
        """
        Rollback: drop all deltas with position > pos.
        """
        self.entries = [(p, h, dK, dV) for (p, h, dK, dV) in self.entries if p <= pos]

    def clear_all(self):
        self.entries.clear()


class DeltaKVEngine:
    """
    KV-cache delta engine:
    - Holds a MasterKVCache
    - Holds a DeltaKVCache
    - Reconstructs effective KV for attention
    """

    def __init__(self, master_kv: MasterKVCache, delta_kv: Optional[DeltaKVCache] = None):
        self.master_kv = master_kv
        self.delta_kv = delta_kv or DeltaKVCache()

    def get_effective_kv(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Reconstruct full effective KV:
        K_eff = K_master + sum(deltas)
        V_eff = V_master + sum(deltas)

        For now, we apply deltas in a simple loop.
        You can optimize this with indexing or sparse tensors.
        """
        K_eff = self.master_kv.K_master.clone()
        V_eff = self.master_kv.V_master.clone()

        # Assume batch size 1 for simplicity: [1, L, H, D]
        # Extend to batch if needed.
        for (pos, head, dK, dV) in self.delta_kv.entries:
            # K_eff[0, pos, head, :] += dK
            # V_eff[0, pos, head, :] += dV
            K_eff[0, pos, head, :] += dK.to(K_eff.device)
            V_eff[0, pos, head, :] += dV.to(V_eff.device)

        return K_eff, V_eff

    def add_token_delta(self,
                        pos: int,
                        delta_K: torch.Tensor,
                        delta_V: torch.Tensor):
        """
        Add deltas for all heads at a given position.
        delta_K: [num_heads, head_dim]
        delta_V: [num_heads, head_dim]
        """
        assert delta_K.shape == delta_V.shape
        num_heads, head_dim = delta_K.shape

        for h in range(num_heads):
            dK_h = delta_K[h]  # [D]
            dV_h = delta_V[h]  # [D]
            self.delta_kv.add_delta(pos=pos, head=h, delta_K=dK_h, delta_V=dV_h)

    def rollback_to(self, pos: int):
        """
        Roll back to a given token position.
        """
        self.delta_kv.clear_after(pos)

    def reset_deltas(self):
        """
        Clear all deltas (e.g., new sequence or new branch).
        """
        self.delta_kv.clear_all()


# ---------------------------------------------------------------------
# Example integration with a simple attention module
# ---------------------------------------------------------------------

class SimpleAttention(torch.nn.Module):
    """
    Minimal attention block that uses the DeltaKVEngine
    to get effective KV instead of a flat KV cache.
    """

    def __init__(self, embed_dim: int, num_heads: int):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        assert self.embed_dim % self.num_heads == 0

        self.W_q = torch.nn.Linear(embed_dim, embed_dim)
        self.W_k = torch.nn.Linear(embed_dim, embed_dim)
        self.W_v = torch.nn.Linear(embed_dim, embed_dim)
        self.W_o = torch.nn.Linear(embed_dim, embed_dim)

    def forward(self,
                x: torch.Tensor,
                kv_engine: DeltaKVEngine):
        """
        x: [batch, seq_len, embed_dim] (current input)
        kv_engine: DeltaKVEngine with master + deltas

        We:
        - compute Q from x
        - get effective K,V from kv_engine
        - run attention
        """
        B, L, D = x.shape
        H = self.num_heads
        Hd = self.head_dim

        # Compute Q from current input
        Q = self.W_q(x)  # [B, L, D]
        Q = Q.view(B, L, H, Hd)

        # Get effective KV from engine
        K_eff, V_eff = kv_engine.get_effective_kv()  # [B, L, H, Hd]

        # Scaled dot-product attention
        # Q: [B, L_q, H, Hd]
        # K_eff: [B, L_k, H, Hd]
        # V_eff: [B, L_k, H, Hd]
        scale = 1.0 / (Hd ** 0.5)

        # [B, H, L_q, L_k]
        attn_scores = torch.einsum("blhd,bLhd->bhll", Q, K_eff) * scale
        attn_weights = torch.softmax(attn_scores, dim=-1)

        # [B, L_q, H, Hd]
        out = torch.einsum("bhll,bLhd->blhd", attn_weights, V_eff)
        out = out.reshape(B, L, D)
        out = self.W_o(out)
        return out


# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------

def example_usage():
    B = 1
    L_master = 8   # base context length
    H = 4
    Hd = 16
    D = H * Hd

    # Create a fake master KV (e.g., from prompt)
    K_master = torch.randn(B, L_master, H, Hd)
    V_master = torch.randn(B, L_master, H, Hd)

    master_cache = MasterKVCache(K_master, V_master)
    delta_cache = DeltaKVCache()
    kv_engine = DeltaKVEngine(master_cache, delta_cache)

    # Create attention block
    attn = SimpleAttention(embed_dim=D, num_heads=H)

    # Current input token(s)
    x = torch.randn(B, 1, D)  # one new token

    # Forward pass using effective KV
    out = attn(x, kv_engine)

    # Suppose we compute new KV for this token and derive deltas
    # For demo, we just fake some deltas:
    new_K = torch.randn(H, Hd)
    new_V = torch.randn(H, Hd)

    # Compute delta vs master at position pos = L_master - 1 (last token)
    pos = L_master - 1
    base_K = K_master[0, pos]  # [H, Hd]
    base_V = V_master[0, pos]  # [H, Hd]

    delta_K = new_K - base_K
    delta_V = new_V - base_V

    # Add deltas to engine
    kv_engine.add_token_delta(pos=pos, delta_K=delta_K, delta_V=delta_V)

    # Next attention call will see updated effective KV
    out2 = attn(x, kv_engine)

    print("out shape:", out.shape)
    print("out2 shape:", out2.shape)


if __name__ == "__main__":
    example_usage()
