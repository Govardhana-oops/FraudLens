"""Security, Privacy & Performance Tests for Module 3."""

import time
import pytest
import numpy as np
from src.interface import tampering_detector

def test_zero_autonomous_fraud_classification_in_module3():
    # Heavily corrupted/spliced image
    np.random.seed(123)
    adversarial_img = np.random.randint(0, 256, (600, 800, 3), dtype=np.uint8)
    res = tampering_detector.analyze(adversarial_img)

    # Status MUST NEVER be FRAUD, CRIMINAL, DETAIN, REJECT, FORGERY
    assert res["status"] not in ["FRAUD", "CRIMINAL", "DETAIN", "REJECT", "FORGERY"]
    assert res["status"] in ["POTENTIAL_TAMPERING", "REVIEW_REQUIRED", "NO_TAMPERING_EVIDENCE"]

def test_forensic_analysis_latency_benchmark():
    card = np.ones((600, 800, 3), dtype=np.uint8) * 235

    # Warmup
    tampering_detector.analyze(card)

    t0 = time.perf_counter()
    iterations = 20
    for _ in range(iterations):
        res = tampering_detector.analyze(card)
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    print(f"\n[MODULE 3 BENCHMARK] Average latency: {avg_ms:.2f} ms/doc")
    assert avg_ms < 150.0, f"Forensic analysis latency too high: {avg_ms:.2f} ms"
