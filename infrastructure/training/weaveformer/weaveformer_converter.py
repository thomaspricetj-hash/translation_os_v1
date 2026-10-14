#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Iterable

import numpy as np
import torch

if TYPE_CHECKING:
    from torch import Tensor

from .base import TextModel, gguf, logger


@TextModel.register("WeaveFormerForCausalLM", "WeaveForCausalLM")
class WeaveFormerModel(TextModel):
    model_arch = gguf.MODEL_ARCH.WEAVE

    def set_gguf_parameters(self):
        super().set_gguf_parameters()

        hparams = self.hparams

        # Basic params
        self.gguf_writer.add_vocab_size(hparams["vocab_size"])
        self.gguf_writer.add_context_length(hparams.get("max_position_embeddings", 512))
        self.gguf_writer.add_embedding_length(hparams["hidden_size"])
        self.gguf_writer.add_feed_forward_length(hparams["intermediate_size"])
        self.gguf_writer.add_block_count(self.block_count)
        self.gguf_writer.add_head_count(hparams["num_attention_heads"])
        self.gguf_writer.add_head_count_kv(hparams.get("num_key_value_heads", hparams["num_attention_heads"]))

        # RoPE
        if rope_dim := hparams.get("head_dim"):
            self.gguf_writer.add_rope_dimension_count(rope_dim)
        else:
            self.gguf_writer.add_rope_dimension_count(hparams["hidden_size"] // hparams["num_attention_heads"])

        self.gguf_writer.add_rope_freq_base(hparams.get("rope_theta", 10000.0))
        self.gguf_writer.add_rope_scaling_type(gguf.RopeScalingType.NONE)

        # Normalization
        self.gguf_writer.add_layer_norm_rms_eps(hparams.get("rms_norm_eps", 1e-6))

    def set_vocab(self):
        """Set vocabulary using the DaxWeaveTokenizer."""
        try:
            from dax.tokenization_weaveformer import DaxWeaveTokenizer

            # Initialize with Qwen base tokenizer
            tokenizer = DaxWeaveTokenizer.from_qwen()

            # Use GPT2-style vocab with our tokenizer
            self._set_vocab_gpt2_tokenizer(tokenizer)
        except Exception as e:
            logger.info(f"DAX tokenizer not available: {e}")
            logger.info("Falling back to Qwen tokenizer for GGUF")
            try:
                self._set_vocab_qwen()
            except Exception:
                # Final fallback - use basic GPT-2 vocab
                self._set_vocab_gpt2()

    def modify_tensors(self, data_torch: Tensor, name: str, bid: int | None) -> Iterable[tuple[str, Tensor]]:
        n_head = self.find_hparam(["n_heads", "num_attention_heads"], optional=True)
        n_kv_head = self.find_hparam(["n_kv_heads", "num_key_value_heads"], optional=True)

        if name.endswith("q_proj.weight"):
            data_torch = self._permute(data_torch, n_head, n_head)
        if name.endswith("k_proj.weight"):
            data_torch = self._permute(data_torch, n_head, n_kv_head)

        # Skip duplicate handling
        if "ffn.ffn_norm" in name:
            return

        # final_proj.weight -> ff_up.weight  
        if "final_proj.weight" in name and "weave_combine" not in name:
            new_name = f"blk.{bid}.ff_up.weight"
            yield (new_name, data_torch)
            return

        # weave_combine.weight -> ff_down.weight
        if "weave_combine.weight" in name:
            new_name = f"blk.{bid}.ff_down.weight"
            yield (new_name, data_torch)
            return

        # branch_projections.*.weight
        if "branch_projections" in name and name.endswith(".weight"):
            parts = name.split(".")
            branch_idx = int(parts[-2].split("_")[-1])
            new_name = f"blk.{bid}.ffn_gate.branch_{branch_idx}.weight"
            yield (new_name, data_torch)
            return

        # branch_projections.*.bias
        if "branch_projections" in name and name.endswith(".bias"):
            parts = name.split(".")
            branch_idx = int(parts[-2].split("_")[-1])
            new_name = f"blk.{bid}.ffn_gate.branch_{branch_idx}.bias"
            yield (new_name, data_torch)
            return

        # lattice_norm.*.weight
        if "lattice_norm" in name and name.endswith(".weight"):
            parts = name.split(".")
            idx = int(parts[-2].split("_")[-1])
            new_name = f"blk.{bid}.ffn_norm_{idx}.weight"
            yield (new_name, data_torch)
            return

        # lattice_proj.*.weight
        if "lattice_proj" in name and name.endswith(".weight"):
            parts = name.split(".")
            idx = int(parts[-2].split("_")[-1])
            new_name = f"blk.{bid}.ffn_gate_{idx}.weight"
            yield (new_name, data_torch)
            return

        # branch_gates
        if "branch_gates" in name:
            new_name = f"blk.{bid}.ffn_gate.gates"
            yield (new_name, data_torch)
            return

        # weave_gates
        if "weave_gates" in name:
            new_name = f"blk.{bid}.ffn_gate.weave_gates"
            yield (new_name, data_torch)
            return

        # final_proj.bias -> ff_up.bias
        if "final_proj.bias" in name:
            new_name = f"blk.{bid}.ff_up.bias"
            yield (new_name, data_torch)
            return

        # weave_combine.bias -> ff_down.bias
        if "weave_combine.bias" in name:
            new_name = f"blk.{bid}.ff_down.bias"
            yield (new_name, data_torch)
            return

        # lattice_norm.*.bias
        if "lattice_norm" in name and name.endswith(".bias"):
            parts = name.split(".")
            idx = int(parts[-2].split("_")[-1])
            new_name = f"blk.{bid}.ffn_norm_{idx}.bias"
            yield (new_name, data_torch)
            return

        # lattice_proj.*.bias
        if "lattice_proj" in name and name.endswith(".bias"):
            parts = name.split(".")
            idx = int(parts[-2].split("_")[-1])
            new_name = f"blk.{bid}.ffn_gate_{idx}.bias"
            yield (new_name, data_torch)
            return

        # Skip duplicate handling
        if name.endswith("ffn.ffn_norm.weight"):
            return

        yield from super().modify_tensors(data_torch, name, bid)

    def _permute(self, weights: Tensor, n_head: int, n_head_kv: int | None) -> Tensor:
        if n_head_kv is not None and n_head != n_head_kv:
            n_head = n_head_kv
        return (weights.reshape(n_head, 2, weights.shape[0] // n_head // 2, *weights.shape[1:])
                .swapaxes(1, 2)
                .reshape(weights.shape))
