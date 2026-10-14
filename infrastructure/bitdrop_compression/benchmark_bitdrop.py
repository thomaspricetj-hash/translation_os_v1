"""
BitDrop Compression V0 Scoreboard Benchmark
"""
import json, time
from pathlib import Path
import sys
sys.path.insert(0, str(Path("TRANSLATION_OS_V1/infrastructure/bitdrop_compression")))
from bitdrop_compression_v0 import compress_text

samples = [
    "The quick brown fox jumps over the lazy dog. " * 20,
    "Photosynthesis is the process plants use to convert sunlight into chemical energy producing glucose and oxygen. " * 30,
    "What is 2+2? What is the capital of France? Explain quantum mechanics in simple terms. " * 10,
]

results = []
for i, s in enumerate(samples):
    start = time.perf_counter()
    res = compress_text(s)
    elapsed = (time.perf_counter() - start) * 1000
    results.append({
        "sample_id": i+1,
        "original_bytes": res["original_bytes"],
        "compressed_bytes": res["compressed_bytes"],
        "compression_ratio": res["compression_ratio"],
        "latency_ms": elapsed
    })

report = {
    "component": "BitDrop Compression V0",
    "samples_tested": len(samples),
    "average_compression_ratio": sum(r["compression_ratio"] for r in results)/len(results),
    "average_latency_ms": sum(r["latency_ms"] for r in results)/len(results),
    "results": results,
    "scoreboard_decision": "PENDING"
}

print(json.dumps(report, indent=2))
with open("TRANSLATION_OS_V1/infrastructure/bitdrop_compression/bitdrop_compression_benchmark.json", "w") as f:
    json.dump(report, f, indent=2)
