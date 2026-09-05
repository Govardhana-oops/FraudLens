"""Unit Tests for Upstream Module 1 Uncertainty Handling & Propagation."""

import pytest
from src.interface import document_validator

def test_module1_review_required_flag_propagation():
    """Module 1 outputs review_required=True (e.g. from optical noise)."""
    payload = {
        "status": "REVIEW_REQUIRED",
        "document_type": {"value": "passport", "confidence": 0.55},
        "fields": {
            "passport_number": {"value": "P12345678", "confidence": 0.60, "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "confidence": 0.60, "status": "VALID"},
            "nationality": {"value": "USA", "confidence": 0.60, "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "confidence": 0.60, "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "confidence": 0.60, "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": True,
        "warnings": ["Low OCR contrast detected"]
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True
    assert any("Low OCR contrast" in w for w in res["warnings"])

def test_unextracted_optional_field_not_penalized_as_invalid():
    """Module 1 omits gender; Module 2 should not fail as syntax error."""
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
            # 'gender' omitted
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "VALID"
    assert "gender" not in res["field_results"] or res["field_results"]["gender"].status in ["VALID", "UNKNOWN"]

def test_module1_unknown_status_graceful_routing():
    """When Module 1 returns unknown due to blur, Module 2 safely outputs UNKNOWN."""
    payload = {
        "status": "UNKNOWN",
        "document_type": {"value": "unknown_document", "confidence": 0.0},
        "fields": {},
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": True,
        "warnings": ["Optical document unidentifiable"]
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True
    assert res["validation_score"] == 0.50
