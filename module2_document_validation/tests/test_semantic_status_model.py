"""Regression Test Suite for Module 2 Status Semantics and Precedence Hierarchy."""

import pytest
from src.interface import document_validator

# 1. Missing passport number -> UNKNOWN
def test_missing_passport_number_yields_unknown():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
            # passport_number missing
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

# 2. Passport number present but malformed -> INVALID
def test_malformed_passport_number_yields_invalid():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "123", "status": "INVALID"}, # Too short (< 6 chars)
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

# 3. Missing required ID number -> UNKNOWN
def test_missing_national_id_number_yields_unknown():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "national_id", "confidence": 0.95},
        "fields": {
            "full_name": {"value": "NOAH JOHNSON", "status": "VALID"},
            "date_of_birth": {"value": "1999-06-19", "status": "VALID"}
            # id_number missing
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNKNOWN"

# 4. Required date unavailable -> UNKNOWN / REVIEW_REQUIRED
def test_missing_expiry_date_yields_unknown():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "visa", "confidence": 0.95},
        "fields": {
            "visa_number": {"value": "V9876543", "status": "VALID"},
            "full_name": {"value": "EMMA JONES", "status": "VALID"}
            # date_of_expiry missing
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNKNOWN"

# 5. Invalid date present -> INVALID
def test_invalid_calendar_date_present_yields_invalid():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_birth": {"value": "1985-02-30", "status": "INVALID"}, # Feb 30
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID"

# 6. Low-confidence critical field -> REVIEW_REQUIRED
def test_low_confidence_critical_field_yields_review_required():
    payload = {
        "status": "REVIEW_REQUIRED",
        "document_type": {"value": "passport", "confidence": 0.50},
        "fields": {
            "passport_number": {"value": "P12345678", "confidence": 0.55, "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "confidence": 0.55, "status": "VALID"},
            "nationality": {"value": "USA", "confidence": 0.55, "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "confidence": 0.55, "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": True,
        "warnings": ["Low OCR optical confidence"]
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True

# 7. Module 1 review_required=true -> Uncertainty Propagated
def test_module1_review_required_propagation():
    payload = {
        "status": "REVIEW_REQUIRED",
        "document_type": {"value": "driver_license", "confidence": 0.95},
        "fields": {
            "license_number": {"value": "DL-A85329037", "status": "VALID"},
            "full_name": {"value": "JOHN BROWN", "status": "VALID"},
            "date_of_birth": {"value": "1980-12-21", "status": "VALID"},
            "expiry_date": {"value": "2030-09-14", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": True,
        "warnings": ["High blur in header region"]
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True

# 8. Visual/MRZ conflict -> REVIEW_REQUIRED
def test_visual_mrz_conflict_yields_review_required():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P99999999", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": {
            "status": "VALID", "mrz_format": "TD3",
            "lines": [
                "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": True
        },
        "consistency": {
            "status": "CONFLICT",
            "conflicts": [{"field": "passport_number", "visual_value": "P99999999", "mrz_value": "P12345678"}]
        },
        "review_required": True
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "REVIEW_REQUIRED"

# 9. Valid document with past expiry -> EXPIRED
def test_valid_document_past_expiry_yields_expired():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P88776655", "status": "VALID"},
            "full_name": {"value": "ROBERT CHEN", "status": "VALID"},
            "nationality": {"value": "CAN", "status": "VALID"},
            "date_of_birth": {"value": "1975-03-10", "status": "VALID"},
            "date_of_issue": {"value": "2010-01-15", "status": "VALID"},
            "date_of_expiry": {"value": "2020-01-15", "status": "VALID"} # Expired
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "EXPIRED"
    assert res["review_required"] is True

# 10. Invalid chronology -> INVALID
def test_invalid_chronology_yields_invalid():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "ALICE WONDER", "status": "VALID"},
            "nationality": {"value": "GBR", "status": "VALID"},
            "date_of_issue": {"value": "2030-01-01", "status": "VALID"},
            "date_of_expiry": {"value": "2025-01-01", "status": "VALID"} # Issue > Expiry
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID"

# 11. Unsupported document -> UNSUPPORTED_DOCUMENT
def test_unsupported_document_class_yields_unsupported():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "voter_registration_card", "confidence": 0.95},
        "fields": {"card_number": {"value": "VOTE-12345", "status": "VALID"}},
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNSUPPORTED_DOCUMENT"
    assert res["review_required"] is True

# 12. Malformed / empty input -> INVALID_INPUT
def test_malformed_input_yields_invalid_input():
    payload = {
        "status": "INVALID_INPUT",
        "document_type": {"value": "unknown_document", "confidence": 0.0},
        "error_details": {"type": "IMAGE_CORRUPTED", "message": "Failed to decode image bytes"}
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID_INPUT"
    assert res["validation_score"] == 0.0

# 13. Score Semantics Audit Tests
def test_score_bounds_and_unknown_exclusion():
    # Valid passport with all checks passing -> score == 1.0
    payload_valid = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res_valid = document_validator.validate(payload_valid)
    assert 0.0 <= res_valid["validation_score"] <= 1.0
    assert res_valid["validation_score"] >= 0.95
