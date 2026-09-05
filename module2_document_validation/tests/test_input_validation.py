"""Unit Tests for Module 2 Input Validation & Schema Ingestion."""

import pytest
from src.interface import document_validator
from src.schemas.input_schema import Module1InputPayload

def test_valid_dict_input():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    result = document_validator.validate(payload)
    assert result["module"] == "module2_document_validation"
    assert result["document_type"] == "passport"
    assert "overall_status" in result
    assert "validation_score" in result

def test_json_string_input():
    json_str = '{"status": "SUCCESS", "document_type": "passport", "fields": {}}'
    result = document_validator.validate(json_str)
    assert result["document_type"] == "passport"

def test_malformed_json_string():
    bad_json = '{status: SUCCESS, invalid_json_syntax'
    result = document_validator.validate(bad_json)
    assert result["overall_status"] == "INVALID_INPUT"
    assert result["review_required"] is True

def test_unsupported_input_type():
    result = document_validator.validate(12345) # integer input
    assert result["overall_status"] == "INVALID_INPUT"

def test_upstream_invalid_input():
    payload = {
        "status": "INVALID_INPUT",
        "document_type": {"value": "unknown_document", "confidence": 0.0},
        "error_details": {"type": "IMAGE_CORRUPT", "message": "Corrupted image file"}
    }
    result = document_validator.validate(payload)
    assert result["overall_status"] == "INVALID_INPUT"
    assert result["review_required"] is True
