#pragma once
#include <vector>
#include <cstdint>
#include <thread>
#include <zlib.h>

#include "bd3d_skimming.hpp"
#include "bd3d_engine.hpp"

namespace syntheticmind {
namespace bd3d {

using ByteVec = std::vector<uint8_t>;

enum BackendTag : uint8_t {
    TAG_ZLIB = 0x01,
    TAG_BD3D = 0x02,
    TAG_SKIM = 0x80
};

struct ChunkHeader {
    uint32_t uncompressed_len;
    uint32_t compressed_len;
    uint32_t chunk_index;
};

struct CompressedChunk {
    uint8_t tag;
    ChunkHeader header;
    ByteVec payload;
};

inline ByteVec zlib_compress(const ByteVec& in) {
    uLongf dest_len = compressBound(in.size());
    ByteVec out(dest_len);
    int res = compress(out.data(), &dest_len, in.data(), in.size());
    if (res != Z_OK) return {};
    out.resize(dest_len);
    return out;
}

inline ByteVec zlib_decompress(const ByteVec& in, size_t expected) {
    ByteVec out(expected);
    uLongf dest_len = expected;
    int res = uncompress(out.data(), &dest_len, in.data(), in.size());
    if (res != Z_OK) return {};
    out.resize(dest_len);
    return out;
}

struct HybridConfig {
    size_t small_threshold  = 512;
    size_t hybrid_threshold = 8192;
    size_t chunk_size       = 4096;
};

struct HybridCompressor {
    BD3DEngine engine;
    HybridConfig cfg;

    CompressedChunk compress_chunk(const ByteVec& in, uint32_t index) {
        CompressedChunk cc;
        cc.header.uncompressed_len = static_cast<uint32_t>(in.size());
        cc.header.chunk_index      = index;

        ByteVec skimmed = skim_encode(in);
        bool skim_applied = (skimmed.size() < in.size());
        const ByteVec& data = skim_applied ? skimmed : in;

        ByteVec compressed;
        uint8_t backend_tag = 0;

        if (data.size() <= cfg.small_threshold) {
            compressed  = zlib_compress(data);
            backend_tag = TAG_ZLIB;
        } else {
            compressed  = engine.encode(data);
            backend_tag = TAG_BD3D;
        }

        cc.header.compressed_len = static_cast<uint32_t>(compressed.size());
        cc.tag    = backend_tag | (skim_applied ? TAG_SKIM : 0);
        cc.payload = std::move(compressed);
        return cc;
    }

    ByteVec decompress_chunk(const CompressedChunk& cc) {
        ByteVec data;
        bool skim_applied = (cc.tag & TAG_SKIM) != 0;
        bool is_zlib      = (cc.tag & TAG_ZLIB) != 0;

        if (is_zlib) {
            data = zlib_decompress(cc.payload, cc.header.uncompressed_len);
        } else {
            data = engine.decode(cc.payload);
        }

        if (skim_applied) {
            data = skim_decode(data);
        }
        return data;
    }

    std::vector<CompressedChunk> compress_grouped_block(const ByteVec& grouped) {
        const size_t n  = grouped.size();
        const size_t cs = cfg.chunk_size;
        size_t num_chunks = (n + cs - 1) / cs;

        std::vector<CompressedChunk> chunks(num_chunks);
        std::vector<std::thread> threads;
        threads.reserve(num_chunks);

        for (size_t i = 0; i < num_chunks; ++i) {
            threads.emplace_back([&, i]() {
                size_t start = i * cs;
                size_t end   = std::min(start + cs, n);
                ByteVec slice(grouped.begin() + start, grouped.begin() + end);
                chunks[i] = compress_chunk(slice, static_cast<uint32_t>(i));
            });
        }

        for (auto& t : threads) t.join();
        return chunks;
    }

    ByteVec decompress_grouped_block(const std::vector<CompressedChunk>& chunks) {
        ByteVec out;
        for (const auto& cc : chunks) {
            ByteVec data = decompress_chunk(cc);
            out.insert(out.end(), data.begin(), data.end());
        }
        return out;
    }

    // simple auto-calibration stub; you can refine this
    void auto_calibrate(const ByteVec& sample) {
        const size_t sizes[] = {1024, 2048, 4096, 8192, 16384};
        size_t best_chunk = cfg.chunk_size;
        size_t best_size  = sample.size();
        for (size_t cs : sizes) {
            cfg.chunk_size = cs;
            auto chunks = compress_grouped_block(sample);
            size_t total = 0;
            for (auto& c : chunks) total += c.header.compressed_len;
            if (total < best_size) {
                best_size  = total;
                best_chunk = cs;
            }
        }
        cfg.chunk_size      = best_chunk;
        cfg.small_threshold = cfg.chunk_size / 8;
        cfg.hybrid_threshold = cfg.chunk_size * 2;
    }
};

} // namespace bd3d
} // namespace syntheticmind