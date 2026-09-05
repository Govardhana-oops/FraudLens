"""Memory Consumption & Leak Detection Benchmark for Module 11."""

import gc
import pytest
import numpy as np
from module7_integration_engine.src.interface import screening_orchestrator
from module11_performance_profiling.src.profiler import PerformanceProfiler

def test_memory_stability_across_repeated_screenings():
    doc_img = np.ones((200, 200, 3), dtype=np.uint8) * 230
    live_img = np.ones((150, 150, 3), dtype=np.uint8) * 220

    # Initial memory
    gc.collect()
    mem_start = PerformanceProfiler.get_process_memory_mb()

    # Execute 50 continuous full-pipeline screenings
    for _ in range(50):
        screening_orchestrator.process_screening(doc_img, live_img)

    gc.collect()
    mem_end = PerformanceProfiler.get_process_memory_mb()

    if mem_start > 0 and mem_end > 0:
        mem_growth_mb = mem_end - mem_start
        print(f"\n[MEMORY PROFILE] Initial: {mem_start:.2f} MB | Final: {mem_end:.2f} MB | Growth: {mem_growth_mb:.2f} MB")
        # Memory growth across 50 runs should be negligible (< 25 MB)
        assert mem_growth_mb < 25.0, f"Potential memory leak detected: {mem_growth_mb:.2f} MB growth"
