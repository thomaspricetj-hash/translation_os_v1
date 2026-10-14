# DAX Token Layer + BitDrop BD3D Hybrid Compression

Complete C++17 implementation of the DAX+BD3D compression system for model runtime optimization.

## Files Created

| File | Purpose |
|------|---------|
| `dax_token_layer.hpp` | Tokenization, delta diffing, GroupIndexer |
| `bd3d_skimming.hpp` | Reversible RLE-like skimming transform |
| `bd3d_engine.hpp` | BD3D 3D bit-drop engine interface (stub) |
| `bd3d_hybrid.hpp` | Hybrid pipeline: chunking + parallel compression |
| `dax_bd3d_api.hpp` | High-level API for model integration |

## System Overview

```
Text → Tokenize → Delta Diff → Group Indexer
                              ↓
                    Hybrid Compressor
                    ├─ Skimming (RLE)
                    ├─ Backend Selection (zlib/BD3D)
                    ├─ Chunking (4KB default)
                    └─ Parallel Threads
                              ↓
                      Compressed Chunks
```

## Usage

### 1. Basic Integration

```cpp
#include "dax_bd3d_api.hpp"

// Create context at startup
syntheticmind::DAXBD3DContext dax_ctx;

// Optional: auto-calibrate for your data
ByteVec sample = /* ... */;
dax_ctx.compressor.auto_calibrate(sample);
```

### 2. Compress KV-cache or Logs

```cpp
std::string master_text = "Previous turn prompt";
std::vector<std::string> target_texts = {
    "Agent response 1",
    "User query 2",
    "Model output 3"
};

auto chunks = syntheticmind::compress_dax_block(
    dax_ctx,
    master_text,
    target_texts
);

// Store `chunks` in your memory engine/KV-cache
```

### 3. Decompress for Reconstruction

```cpp
auto grouped_bytes = syntheticmind::decompress_dax_block(dax_ctx, chunks);

// Rebuild deltas and token streams as needed
```

## Compression Flow

1. **Tokenization**: Converts text to `std::vector<uint32_t>` tokens
2. **Delta Diffing**: Computes signed differences `target - master`
3. **Group Indexer**: Flattens multiple delta streams `[MΔ1][MΔ2]...[MΔN]` into one byte block
4. **Skimming**: Reversible RLE compression (escapes long runs)
5. **Backend Selection**:
   - Small chunks (≤512 bytes) → zlib
   - Large chunks (>512 bytes) → BD3D engine
6. **Parallel Chunking**: Compresses 4KB chunks in parallel using `std::thread`
7. **Tagging**: Each chunk tagged with backend and skimming flags

## Build Requirements

```bash
g++ -std=c++17 -O2 your_file.cpp dax_*.hpp bd3d_*.hpp -lz -pthread
```

Or add headers directly to your project (header-only design).

## API Reference

### `DAXBD3DContext`
Holds tokenizer, indexer, and compressor instances.

### `compress_dax_block(ctx, master_text, target_texts)`
- **Input**: Master text + vector of target texts
- **Output**: Vector of `CompressedChunk` objects

### `decompress_dax_block(ctx, chunks)`
- **Input**: Vector of `CompressedChunk` objects
- **Output**: Decompressed byte block (grouped deltas)

## Compression Tags

| Tag | Value | Meaning |
|-----|-------|---------|
| `TAG_ZLIB` | 0x01 | zlib compression used |
| `TAG_BD3D` | 0x02 | BD3D engine used |
| `TAG_SKIM` | 0x80 | Skimming transform applied |

## HybridConfig Tuning

```cpp
HybridCompressor& comp = dax_ctx.compressor;
comp.cfg.small_threshold    = 512;   // Use zlib for chunks ≤ this
comp.cfg.hybrid_threshold   = 8192;  // Threshold for hybrid decisions
comp.cfg.chunk_size         = 4096;  // Chunk size in bytes
```

## Integration Points

| Component | Compression Hook |
|-----------|------------------|
| **KV-cache** | Compress master + new token stream |
| **Memory Engine** | Store compressed deltas as long-term state |
| **Agent Logs** | Serialize via `compress_dax_block()` |

## Notes

- The BD3D engine is currently a pass-through placeholder - implement your 3D bit-drop algorithm in `bd3d_engine.hpp`
- Delta bytes use low-byte projection (`v & 0xFF`) - refine this for better compression
- Skimming escapes runs of 4+ identical bytes or the escape byte itself (0xFF)

## License

MIT