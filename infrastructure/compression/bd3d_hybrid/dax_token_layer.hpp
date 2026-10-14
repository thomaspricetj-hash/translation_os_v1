#pragma once
#include <vector>
#include <string>
#include <cstdint>
#include <algorithm>

namespace syntheticmind {
namespace dax {

using Token      = uint32_t;
using TokenStream = std::vector<Token>;
using Delta      = std::vector<int32_t>;
using ByteVec    = std::vector<uint8_t>;

struct StubTokenizer {
    TokenStream tokenize(const std::string& text) {
        TokenStream out;
        out.reserve(text.size());
        for (char c : text) {
            out.push_back(static_cast<Token>(static_cast<uint8_t>(c)));
        }
        return out;
    }
};

inline Delta diff(const TokenStream& master, const TokenStream& target) {
    const size_t n = std::max(master.size(), target.size());
    Delta d;
    d.reserve(n);
    for (size_t i = 0; i < n; ++i) {
        int32_t m = (i < master.size()) ? static_cast<int32_t>(master[i]) : 0;
        int32_t t = (i < target.size()) ? static_cast<int32_t>(target[i]) : 0;
        d.push_back(t - m);
    }
    return d;
}

struct GroupIndexer {
    ByteVec group(const std::vector<Delta>& deltas) {
        ByteVec out;
        for (const auto& d : deltas) {
            for (int32_t v : d) {
                // simple low-byte projection; you can refine this later
                out.push_back(static_cast<uint8_t>(v & 0xFF));
            }
        }
        return out;
    }
};

} // namespace dax
} // namespace syntheticmind