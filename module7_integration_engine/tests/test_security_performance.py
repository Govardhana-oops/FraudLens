"""Security, Non-Exclusion & Latency Benchmark Tests for Module 7."""

import time
import pytest
import numpy as np
from src.interface import screening_orchestrator

def test_zero_autonomous_fraud_decision_in_module7():
    # Corrupted inputs across all layers
    doc_arr = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
    res = screening_orchestrator.process_screening(doc_arr)

    # Output must strictly NOT contain FRAUD, CRIMINAL, DETAIN, REJECT, FORGERY
    assert res["recommended_action"] not in ["FRAUD", "CRIMINAL", "DETAIN", "REJECT", "FORGERY"]
    assert res["recommended_action"] in [
        "CLEAR", "STANDARD_INSPECTION", "SECONDARY_INSPECTION_RECOMMENDED",
        "TECHNICAL_REVIEW_REQUIRED", "RECAPTURE_REQUIRED"
    ]

def test_full_pipeline_latency_benchmark():
    doc_arr = np.ones((200, 200, 3), dtype=np.uint8) * 230
    live_arr = np.ones((200, 200, 3), dtype=np.uint8) * 230

    # Warmup
    screening_orchestrator.process_screening(doc_arr, live_arr)

    t0 = time.perf_counter()
    iterations = 20
    for _ in range(iterations):
        res = screening_orchestrator.process_screening(doc_arr, live_arr)
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    print(f"\n[MODULE 7 BENCHMARK] Average Full End-to-End Pipeline Latency: {avg_ms:.2f} ms/passenger")
    assert avg_ms < 150.0, f"Total pipeline latency too high: {avg_ms:.2f} ms"
