"""Security, Privacy & Adversarial Robustness Test Suite for Module 2."""

import pytest
from src.interface import document_validator

# 1. SQL Injection / Command Injection in text fields
@pytest.mark.parametrize("injection_str", [
    "'; DROP TABLE users; --",
    "P12345678' OR '1'='1",
    "<script>alert('xss')</script>",
    "../../../../etc/passwd",
    "$(reboot)",
    "`rm -rf /`",
    "%00%00%00"
])
def test_injection_strings_handled_safely_as_text(injection_str):
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": injection_str, "status": "VALID"},
            "full_name": {"value": f"ATTACKER {injection_str}", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    # Must not raise unhandled exception and must not execute
    res = document_validator.validate(payload)
    assert res["overall_status"] in ["INVALID", "REVIEW_REQUIRED", "VALID"]
    assert "module" in res

# 2. Oversized Payload (100KB field string)
def test_oversized_payload_resilience():
    huge_string = "A" * 100000
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": huge_string, "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID" # Fails syntax check safely without crashing

# 3. Path Traversal & Special File Names
def test_path_traversal_payload():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "..\\..\\windows\\system32\\cmd.exe", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] in ["INVALID", "UNKNOWN"]

# 4. Zero Autonomous Criminal / Fraud Classification Verification
def test_zero_autonomous_fraud_classification_under_adversarial_input():
    adversarial_payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "FRAUDULENT_DOCUMENT_999", "status": "INVALID"},
            "full_name": {"value": "WANTED_CRIMINAL_NAME", "status": "INVALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONFLICT", "conflicts": [{"field": "doc_num", "visual_value": "A", "mrz_value": "B"}]},
        "review_required": True
    }
    res = document_validator.validate(adversarial_payload)
    # The output MUST NOT be FRAUD, CRIMINAL, DETAIN, REJECT
    assert res["overall_status"] not in ["FRAUD", "CRIMINAL", "DETAIN", "REJECT"]
    assert res["overall_status"] in ["INVALID", "REVIEW_REQUIRED"]
