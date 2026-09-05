"""Concurrent Multi-Threaded Stress Test for Module 10."""

import concurrent.futures
import time
import pytest
import numpy as np
from module7_integration_engine.src.interface import screening_orchestrator
from module10_system_test_matrix.src.generators.scenario_generator import ScenarioGenerator

def _run_single_screening(i: int):
    doc_img = ScenarioGenerator.create_synthetic_passport_image(f"PASS{i:04d}")
    return screening_orchestrator.process_screening(doc_img)

def test_high_volume_concurrent_screening_stress():
    num_threads = 10
    total_requests = 20

    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(_run_single_screening, i) for i in range(total_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    t1 = time.perf_counter()

    assert len(results) == total_requests
    for r in results:
        assert "screening_id" in r
        assert 0.0 <= r["risk_index"] <= 1.0

    total_time_s = t1 - t0
    rps = total_requests / total_time_s
    print(f"\n[MODULE 10 BENCHMARK] Concurrent Throughput: {rps:.2f} passengers/second across {num_threads} workers")
    assert rps > 0.05, f"Concurrency throughput too low: {rps:.2f} req/s"
