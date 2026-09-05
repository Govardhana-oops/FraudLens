"""Full End-to-End Latency Percentiles Benchmarking for Module 11."""

import pytest
import numpy as np
from module7_integration_engine.src.interface import screening_orchestrator
from module11_performance_profiling.src.profiler import PerformanceProfiler

def test_full_pipeline_latency_percentiles():
    doc_img = np.ones((200, 200, 3), dtype=np.uint8) * 230
    live_img = np.ones((150, 150, 3), dtype=np.uint8) * 220

    stats = PerformanceProfiler.measure_latency_percentiles(
        lambda: screening_orchestrator.process_screening(doc_img, live_img),
        iterations=30,
        warmup=5
    )

    print(f"\n=======================================================")
    print(f" AI-DIDSS FULL SYSTEM LATENCY PERCENTILE BENCHMARK (N=30)")
    print(f"=======================================================")
    print(f" Mean Latency:  {stats['mean_ms']:.2f} ms")
    print(f" P50 (Median):  {stats['p50_ms']:.2f} ms")
    print(f" P90:           {stats['p90_ms']:.2f} ms")
    print(f" P95:           {stats['p95_ms']:.2f} ms")
    print(f" P99:           {stats['p99_ms']:.2f} ms")
    print(f"=======================================================")

    assert stats["p95_ms"] < 150.0, f"P95 SLA exceeded: {stats['p95_ms']} ms"
    assert stats["p99_ms"] < 250.0, f"P99 SLA exceeded: {stats['p99_ms']} ms"
