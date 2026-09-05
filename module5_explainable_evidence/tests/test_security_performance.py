"""Security, Privacy & Performance Tests for Module 5."""

import time
import pytest
from src.interface import evidence_fusion_engine

def test_zero_autonomous_fraud_decision_in_module5():
    # Heavily corrupted/adversarial dossier
    m2 = {"overall_status": "INVALID", "errors": ["MALFORMED_FORGERY"]}
    m3 = {"status": "POTENTIAL_TAMPERING", "anomaly_score": 0.99, "tampering_types_detected": ["photo_substitution"]}
    m4 = {"status": "NO_MATCH", "similarity_score": 0.05}

    res = evidence_fusion_engine.assess(None, m2, m3, m4)
    # Output must strictly NOT contain FRAUD, CRIMINAL, DETAIN, REJECT, FORGERY
    assert res["recommended_action"] not in ["FRAUD", "CRIMINAL", "DETAIN", "REJECT", "FORGERY"]
    assert res["recommended_action"] in ["SECONDARY_INSPECTION_RECOMMENDED", "TECHNICAL_REVIEW_REQUIRED"]

def test_evidence_fusion_latency_benchmark():
    m1 = {"status": "SUCCESS", "document_type": {"value": "passport", "confidence": 0.98}}
    m2 = {"overall_status": "VALID", "validation_score": 1.0}
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "anomaly_score": 0.10}
    m4 = {"status": "MATCH", "similarity_score": 0.90}

    # Warmup
    evidence_fusion_engine.assess(m1, m2, m3, m4)

    t0 = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        res = evidence_fusion_engine.assess(m1, m2, m3, m4)
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    print(f"\n[MODULE 5 BENCHMARK] Average latency: {avg_ms:.3f} ms/dossier")
    assert avg_ms < 10.0, f"Evidence fusion latency too high: {avg_ms:.3f} ms"
