"""Unit Tests for Module 5 Public Interface."""

import pytest
from src.interface import evidence_fusion_engine

def test_interface_full_valid_dossier():
    m1 = {"status": "SUCCESS", "document_type": {"value": "passport", "confidence": 0.98}}
    m2 = {"overall_status": "VALID", "validation_score": 1.0, "errors": [], "warnings": []}
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "anomaly_score": 0.10, "tampering_types_detected": []}
    m4 = {"status": "MATCH", "similarity_score": 0.92, "warnings": []}

    res = evidence_fusion_engine.assess(m1, m2, m3, m4)
    assert res["module"] == "module5_explainable_evidence"
    assert res["recommended_action"] == "CLEAR"
    assert res["risk_index"] < 0.20
    assert res["review_required"] is False
    assert len(res["itemized_evidence"]["positive_findings"]) >= 2

def test_interface_null_modules_fallback():
    # Empty inputs must not crash
    res = evidence_fusion_engine.assess()
    assert res["recommended_action"] in ["CLEAR", "TECHNICAL_REVIEW_REQUIRED", "STANDARD_INSPECTION"]
    assert 0.0 <= res["risk_index"] <= 1.0
