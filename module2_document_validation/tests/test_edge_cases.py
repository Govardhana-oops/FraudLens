"""Parameterized & Edge-Case Unit Tests for Module 2 Document Validation."""

import pytest
from datetime import date
from src.validators.date_validator import DateValidator
from src.interface import document_validator
from src.schemas.input_schema import Module1InputPayload, Module1Field, Module1DocumentType

@pytest.mark.parametrize("test_date,expected_status", [
    ("2000-02-29", "PASS"), # Leap year century
    ("2024-02-29", "PASS"), # Normal leap year
    ("2023-02-29", "FAIL"), # Non-leap year -> Invalid
    ("1900-02-29", "FAIL"), # 1900 not leap year (century rule)
    ("2020-04-31", "FAIL"), # April has 30 days
    ("2020-12-31", "PASS"), # Dec 31
    ("2020-00-15", "FAIL"), # Month 0
    ("2020-13-15", "FAIL"), # Month 13
    ("2020-05-00", "FAIL"), # Day 0
    ("2020-05-32", "FAIL"), # Day 32
])
def test_calendar_edge_cases(test_date, expected_status):
    val = DateValidator(reference_date=date(2026, 9, 2))
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={"date_of_birth": Module1Field(value=test_date)}
    )
    checks = val.validate(payload)
    chk = next(c for c in checks if c.field_name == "date_of_birth")
    assert chk.status == expected_status

def test_extreme_whitespace_padding():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "  passport  ", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "   P12345678   ", "status": "VALID"},
            "full_name": {"value": "\t\n  JOHN SMITH  \n", "status": "VALID"},
            "nationality": {"value": " USA ", "status": "VALID"},
            "date_of_birth": {"value": " 1985-04-12 ", "status": "VALID"},
            "date_of_expiry": {"value": " 2030-08-25 ", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "VALID"
    assert res["document_type"] == "passport"

def test_unicode_accents_and_special_names():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOSÉ MARÍA AZNAR-LÓPEZ", "status": "VALID"},
            "nationality": {"value": "ESP", "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "VALID"

def test_null_and_empty_fields_resilience():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": None, "status": "UNKNOWN"},
            "full_name": {"value": "", "status": "UNKNOWN"},
            "nationality": None
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "UNKNOWN" # Missing mandatory primary identifier
    assert res["review_required"] is True
