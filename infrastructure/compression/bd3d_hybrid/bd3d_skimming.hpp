#pragma once
#include <vector>
#include <cstdint>

namespace syntheticmind {
namespace bd3d {

using ByteVec = std::vector<uint8_t>;
static constexpr uint8_t ESC = 0xFF;

inline ByteVec skim_encode(const ByteVec& in) {
    ByteVec out;
    out.reserve(in.size());
    size_t i = 0;
    while (i < in.size()) {
        uint8_t v = in[i];
        size_t run = 1;
        while (i + run < in.size() && in[i + run] == v && run < 255) {
            ++run;
        }
        if (run >= 4 || v == ESC) {
            out.push_back(ESC);
            out.push_back(v);
            out.push_back(static_cast<uint8_t>(run));
        } else {
            for (size_t r = 0; r < run; ++r) {
                out.push_back(v);
            }
        }
        i += run;
    }
    return out;
}

inline ByteVec skim_decode(const ByteVec& in) {
    ByteVec out;
    out.reserve(in.size());
    size_t i = 0;
    while (i < in.size()) {
        uint8_t v = in[i];
        if (v == ESC && i + 2 < in.size()) {
            uint8_t val = in[i + 1];
            uint8_t run = in[i + 2];
            for (uint8_t r = 0; r < run; ++r) {
                out.push_back(val);
            }
            i += 3;
        } else {
            out.push_back(v);
            ++i;
        }
    }
    return out;
}

} // namespace bd3d
} // namespace syntheticmind