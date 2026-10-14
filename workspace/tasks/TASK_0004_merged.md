# Task ID: TASK_0004
# Original Task: Test sandbox workflow for GPU support
# Merged At: 2026-10-14T12:51:41.712466

[PLANNING]
Need: Nvidia support, AMD support, CPU fallback. Steps: detect hardware, select backend, benchmark.

GPU support plan: detect hardware, select backend, benchmark

---

[CODING]
Implement hardware detection in gpu_detector.py. Load cuda/hip/cpu backend based on detection.