"""Security, Privacy & Performance Benchmark for Module 4."""

import time
import pytest
import numpy as np
from src.interface import face_verifier
from tests.test_interface import _create_synthetic_face

def test_zero_autonomous_criminal_decision_in_module4():
    # Imposter face pair
    face_a = _create_synthetic_face(skin_val=120)
    face_b = _create_synthetic_face(skin_val=220)

    res = face_verifier.verify(face_a, face_b)
    # Output must strictly NOT contain FRAUD, CRIMINAL, DETAIN, IMPOSTER, REJECT
    assert res["status"] not in ["FRAUD", "CRIMINAL", "DETAIN", "IMPOSTER", "REJECT"]
    assert res["status"] in ["MATCH", "NO_MATCH", "REVIEW_REQUIRED"]

def test_biometric_verification_latency_benchmark():
    face = _create_synthetic_face()

    # Warmup
    face_verifier.verify(face, face)

    t0 = time.perf_counter()
    iterations = 20
    for _ in range(iterations):
        res = face_verifier.verify(face, face)
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    print(f"\n[MODULE 4 BENCHMARK] Average latency: {avg_ms:.2f} ms/pair")
    assert avg_ms < 80.0, f"Biometric verification latency too high: {avg_ms:.2f} ms"
