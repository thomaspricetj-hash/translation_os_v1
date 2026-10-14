"""
GPU Detector for Translation OS v1
Detects NVIDIA, AMD, CPU fallback
"""
import json
import subprocess
from pathlib import Path

def detect_nvidia():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().splitlines()
            gpu_name = lines[0].split(',')[0]
            return {"backend": "cuda", "gpu_name": gpu_name.strip(), "vram_gb": "unknown"}
    except Exception:
        pass
    return None

def detect_amd():
    try:
        # Check for rocminfo
        result = subprocess.run(
            ["rocminfo"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "gfx" in result.stdout.lower():
            return {"backend": "hip", "gpu_name": "AMD GPU", "vram_gb": "unknown"}
    except Exception:
        pass
    return None

def detect_cpu():
    return {"backend": "cpu", "gpu_name": "CPU", "vram_gb": "N/A"}

def detect():
    nvidia = detect_nvidia()
    if nvidia:
        return nvidia
    amd = detect_amd()
    if amd:
        return amd
    return detect_cpu()

if __name__ == "__main__":
    info = detect()
    print(json.dumps(info, indent=2))
    # Save report
    Path("TRANSLATION_OS_V1/reports/gpu_detection_report.json").write_text(json.dumps(info, indent=2))
