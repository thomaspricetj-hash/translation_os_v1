#pragma once
#include "dax_token_layer.hpp"
#include "bd3d_hybrid.hpp"

namespace syntheticmind {

struct DAXBD3DContext {
    dax::StubTokenizer tokenizer;
    dax::GroupIndexer  indexer;
    bd3d::HybridCompressor compressor;
};

inline std::vector<bd3d::CompressedChunk>
compress_dax_block(DAXBD3DContext& ctx,
                   const std::string& master_text,
                   const std::vector<std::string>& target_texts) {
    auto master = ctx.tokenizer.tokenize(master_text);

    std::vector<dax::Delta> deltas;
    deltas.reserve(target_texts.size());
    for (const auto& t : target_texts) {
        auto ts = ctx.tokenizer.tokenize(t);
        deltas.push_back(dax::diff(master, ts));
    }

    auto grouped = ctx.indexer.group(deltas);
    // optional: auto-calibrate once on a sample
    // ctx.compressor.auto_calibrate(grouped);
    return ctx.compressor.compress_grouped_block(grouped);
}

inline bd3d::ByteVec
decompress_dax_block(DAXBD3DContext& ctx,
                     const std::vector<bd3d::CompressedChunk>& chunks) {
    return ctx.compressor.decompress_grouped_block(chunks);
}

} // namespace syntheticmind