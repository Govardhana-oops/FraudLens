"""Comprehensive End-to-End Tests for RuleEngine across 44 Test Fixtures."""

import json
import os
import pytest
from src.interface import document_validator

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_cases")

def load_fixture(name: str):
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 1. Passports
def test_valid_passport():
    res = document_validator.validate(load_fixture("valid_passport.json"))
    assert res["overall_status"] == "VALID"
    assert res["validation_score"] >= 0.95
    assert res["review_required"] is False

def test_passport_invalid_number_syntax():
    res = document_validator.validate(load_fixture("passport_invalid_number_syntax.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_passport_missing_number():
    res = document_validator.validate(load_fixture("passport_missing_number.json"))
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

def test_passport_invalid_dob_calendar():
    res = document_validator.validate(load_fixture("passport_invalid_dob_calendar.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_expired_passport():
    res = document_validator.validate(load_fixture("expired_passport.json"))
    assert res["overall_status"] == "EXPIRED"
    assert res["review_required"] is True

def test_passport_issue_after_expiry():
    res = document_validator.validate(load_fixture("passport_issue_after_expiry.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_passport_dob_after_issue():
    res = document_validator.validate(load_fixture("passport_dob_after_issue.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_mrz_checksum_error():
    res = document_validator.validate(load_fixture("mrz_checksum_error.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_visual_mrz_conflict():
    res = document_validator.validate(load_fixture("visual_mrz_conflict.json"))
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True

def test_passport_visual_mrz_dob_conflict():
    res = document_validator.validate(load_fixture("passport_visual_mrz_dob_conflict.json"))
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True

# 2. Visas
def test_valid_visa():
    res = document_validator.validate(load_fixture("valid_visa.json"))
    assert res["overall_status"] == "VALID"
    assert res["validation_score"] >= 0.85

def test_visa_invalid_number():
    res = document_validator.validate(load_fixture("visa_invalid_number.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_visa_expired():
    res = document_validator.validate(load_fixture("visa_expired.json"))
    assert res["overall_status"] == "EXPIRED"
    assert res["review_required"] is True

def test_visa_invalid_stay_dates():
    res = document_validator.validate(load_fixture("visa_invalid_stay_dates.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_visa_missing_expiry():
    res = document_validator.validate(load_fixture("visa_missing_expiry.json"))
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

def test_visa_low_confidence_m1():
    res = document_validator.validate(load_fixture("visa_low_confidence_m1.json"))
    assert res["overall_status"] in ["REVIEW_REQUIRED", "UNKNOWN"]
    assert res["review_required"] is True

def test_visa_mrv_checksum_error():
    res = document_validator.validate(load_fixture("visa_mrv_checksum_error.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

# 3. Driver's Licenses
def test_valid_driver_license():
    res = document_validator.validate(load_fixture("valid_driver_license.json"))
    assert res["overall_status"] == "VALID"

def test_dl_malformed_number():
    res = document_validator.validate(load_fixture("dl_malformed_number.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_dl_missing_number():
    res = document_validator.validate(load_fixture("dl_missing_number.json"))
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

def test_dl_underage_driver():
    res = document_validator.validate(load_fixture("dl_underage_driver.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_dl_expired():
    res = document_validator.validate(load_fixture("dl_expired.json"))
    assert res["overall_status"] == "EXPIRED"
    assert res["review_required"] is True

def test_dl_unknown_jurisdiction():
    res = document_validator.validate(load_fixture("dl_unknown_jurisdiction.json"))
    assert res["overall_status"] == "VALID"

def test_dl_impossible_chronology():
    res = document_validator.validate(load_fixture("dl_impossible_chronology.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

# 4. National IDs
def test_valid_national_id():
    res = document_validator.validate(load_fixture("valid_national_id.json"))
    assert res["overall_status"] == "VALID"

def test_national_id_malformed_mrz_length():
    res = document_validator.validate(load_fixture("national_id_malformed_mrz_length.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_national_id_checksum_error():
    res = document_validator.validate(load_fixture("national_id_checksum_error.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_national_id_visual_mrz_conflict():
    res = document_validator.validate(load_fixture("national_id_visual_mrz_conflict.json"))
    assert res["overall_status"] == "REVIEW_REQUIRED"
    assert res["review_required"] is True

def test_national_id_missing_id():
    res = document_validator.validate(load_fixture("national_id_missing_id.json"))
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

def test_national_id_invalid_dob():
    res = document_validator.validate(load_fixture("national_id_invalid_dob.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

# 5. Permits
def test_valid_permit():
    res = document_validator.validate(load_fixture("valid_permit.json"))
    assert res["overall_status"] == "VALID"

def test_permit_invalid_category():
    res = document_validator.validate(load_fixture("permit_invalid_category.json"))
    assert res["overall_status"] == "VALID" # Emits warning, not fatal
    assert any("non-standard" in w or "Permit category" in w for w in res["warnings"])

def test_permit_expired():
    res = document_validator.validate(load_fixture("permit_expired.json"))
    assert res["overall_status"] == "EXPIRED"
    assert res["review_required"] is True

def test_permit_missing_permit_num():
    res = document_validator.validate(load_fixture("permit_missing_permit_num.json"))
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

def test_permit_issue_after_expiry():
    res = document_validator.validate(load_fixture("permit_issue_after_expiry.json"))
    assert res["overall_status"] == "INVALID"
    assert res["review_required"] is True

def test_permit_non_standard_category_warning():
    res = document_validator.validate(load_fixture("permit_non_standard_category_warning.json"))
    assert res["overall_status"] == "VALID"

# 6. Generic & Edge Cases
def test_malformed_input():
    res = document_validator.validate(load_fixture("malformed_input.json"))
    assert res["overall_status"] == "INVALID_INPUT"

def test_empty_input():
    res = document_validator.validate(load_fixture("empty_input.json"))
    assert res["overall_status"] == "INVALID_INPUT"

def test_unknown_document():
    res = document_validator.validate(load_fixture("unknown_document.json"))
    assert res["overall_status"] == "UNKNOWN"
    assert res["review_required"] is True

def test_unsupported_document_type():
    res = document_validator.validate(load_fixture("unsupported_document_type.json"))
    assert res["overall_status"] == "UNSUPPORTED_DOCUMENT"
    assert res["review_required"] is True

def test_edge_leap_day_valid():
    res = document_validator.validate(load_fixture("edge_leap_day_valid.json"))
    assert res["overall_status"] == "VALID"

def test_edge_leap_day_invalid_nonleap():
    res = document_validator.validate(load_fixture("edge_leap_day_invalid_nonleap.json"))
    assert res["overall_status"] == "INVALID"

def test_edge_whitespace_resilience():
    res = document_validator.validate(load_fixture("edge_whitespace_resilience.json"))
    assert res["overall_status"] == "VALID"

def test_edge_unicode_name_handling():
    res = document_validator.validate(load_fixture("edge_unicode_name_handling.json"))
    assert res["overall_status"] == "VALID"

def test_zero_autonomous_fraud_tagging_across_all():
    all_fixtures = [f for f in os.listdir(FIXTURES_DIR) if f.endswith(".json")]
    for f in all_fixtures:
        res = document_validator.validate(load_fixture(f))
        assert res["overall_status"] not in ["FRAUD", "CRIMINAL", "REJECT", "DETAIN"]
