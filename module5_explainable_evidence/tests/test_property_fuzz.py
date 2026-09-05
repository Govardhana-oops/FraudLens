"""Property & Fuzz Testing for Module 5 Evidence Fusion."""

import random
import pytest
from src.interface import evidence_fusion_engine

@pytest.mark.parametrize("seed", range(15))
def test_fuzz_random_multi_module_scores(seed):
    random.seed(seed)

    m1_statuses = ["SUCCESS", "PARTIAL", "UNKNOWN", "REVIEW_REQUIRED"]
    m2_statuses = ["VALID", "INVALID", "EXPIRED", "REVIEW_REQUIRED", "UNKNOWN", "UNSUPPORTED_DOCUMENT"]
    m3_statuses = ["NO_TAMPERING_EVIDENCE", "POTENTIAL_TAMPERING", "REVIEW_REQUIRED", "UNKNOWN"]
    m4_statuses = ["MATCH", "NO_MATCH", "REVIEW_REQUIRED", "POOR_QUALITY", "NO_FACE_DETECTED", "SPOOF_ATTEMPT_DETECTED"]

    m1 = {"status": random.choice(m1_statuses), "document_type": {"value": "passport", "confidence": random.random()}}
    m2 = {"overall_status": random.choice(m2_statuses), "validation_score": random.random()}
    m3 = {"status": random.choice(m3_statuses), "anomaly_score": random.random()}
    m4 = {"status": random.choice(m4_statuses), "similarity_score": random.random()}

    res = evidence_fusion_engine.assess(m1, m2, m3, m4)
    assert 0.0 <= res["risk_index"] <= 1.0
    assert 0.0 <= res["confidence_score"] <= 1.0
    assert res["recommended_action"] in [
        "CLEAR", "STANDARD_INSPECTION", "SECONDARY_INSPECTION_RECOMMENDED",
        "TECHNICAL_REVIEW_REQUIRED", "RECAPTURE_REQUIRED"
    ]

def test_evidence_determinism_invariant():
    m1 = {"status": "SUCCESS", "document_type": {"value": "passport", "confidence": 0.95}}
    m2 = {"overall_status": "VALID", "validation_score": 0.98}
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "anomaly_score": 0.08}
    m4 = {"status": "MATCH", "similarity_score": 0.88}

    res1 = evidence_fusion_engine.assess(m1, m2, m3, m4)
    res2 = evidence_fusion_engine.assess(m1, m2, m3, m4)

    assert res1["recommended_action"] == res2["recommended_action"]
    assert res1["risk_index"] == res2["risk_index"]
    assert res1["executive_summary"] == res2["executive_summary"]
