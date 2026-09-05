"""High-Precision Latency & Memory Footprint Profiling Engine."""

import time
import os
import gc
from typing import Callable, Any, Dict, List
import numpy as np

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

class PerformanceProfiler:
    """Executes high-resolution timing and memory consumption benchmarking."""

    @staticmethod
    def measure_latency_percentiles(func: Callable[[], Any], iterations: int = 50, warmup: int = 5) -> Dict[str, float]:
        """Runs warmup and timed iterations, returning statistics and percentiles in milliseconds."""
        # 1. Warmup
        for _ in range(warmup):
            func()

        # 2. Benchmark
        latencies = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            func()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

        lat_arr = np.array(latencies)
        return {
            "iterations": iterations,
            "mean_ms": float(np.mean(lat_arr)),
            "std_ms": float(np.std(lat_arr)),
            "min_ms": float(np.min(lat_arr)),
            "max_ms": float(np.max(lat_arr)),
            "p50_ms": float(np.percentile(lat_arr, 50)),
            "p90_ms": float(np.percentile(lat_arr, 90)),
            "p95_ms": float(np.percentile(lat_arr, 95)),
            "p99_ms": float(np.percentile(lat_arr, 99))
        }

    @staticmethod
    def get_process_memory_mb() -> float:
        """Returns current process Resident Set Size (RSS) memory in megabytes."""
        if _HAS_PSUTIL:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        return 0.0
