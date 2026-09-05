"""Test Suite for Document-Type Ambiguity & Classification Confidence in Module 2."""

import pytest
from src.interface import document_validator

def test_low_confidence_document_type_restricts_to_universal_rules():
    """When document_type confidence is low (e.g. 0.50), strict doc-specific mandatory checks are skipped."""
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.50}, # Low confidence (< 0.70)
        "fields": {
            # Note: passport_number is absent, but because doc_type is ambiguous, it shouldn't fail as missing passport
            "date_of_birth": {"value": "1990-05-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-05-12", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True
    assert res["validation_metadata"]["is_doc_type_ambiguous"] is True
    assert any(c["rule_id"] == "AMBIGUITY_DOCUMENT_TYPE_CONFIDENCE" for c in res["checks"])

def test_low_confidence_document_type_with_invalid_date_still_invalid():
    """Even if document_type is ambiguous, fundamental universal calendar violations still fail as INVALID."""
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "visa", "confidence": 0.45},
        "fields": {
            "date_of_birth": {"value": "1990-02-30", "status": "INVALID"}, # Feb 30 impossible
            "date_of_expiry": {"value": "2030-05-12", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_high_confidence_unknown_document_type_yields_unknown():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "unknown_document", "confidence": 0.95},
        "fields": {
            "date_of_birth": {"value": "1990-05-12", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNKNOWN"
    assert res["validation_score"] == 0.50

def test_visa_classified_with_high_confidence_runs_visa_rules():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "visa", "confidence": 0.95},
        "fields": {
            "visa_number": {"value": "V1234567", "status": "VALID"},
            "date_of_expiry": {"value": "2028-10-10", "status": "VALID"},
            "entries": {"value": "MULTIPLE", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "VALID"
    assert res["validation_score"] >= 0.85
