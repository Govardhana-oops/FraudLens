"""Unit Tests for DateValidator and Chronological Sequencing."""

from datetime import date
from src.validators.date_validator import DateValidator
from src.schemas.input_schema import Module1InputPayload, Module1Field, Module1DocumentType

def test_valid_calendar_date():
    validator = DateValidator(reference_date=date(2026, 9, 2))
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_birth": Module1Field(value="1990-05-15"),
            "date_of_issue": Module1Field(value="2020-01-10"),
            "date_of_expiry": Module1Field(value="2030-01-10")
        }
    )
    checks = validator.validate(payload)
    assert all(c.status == "PASS" for c in checks)

def test_invalid_calendar_day():
    validator = DateValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_birth": Module1Field(value="1990-02-30") # Feb 30 does not exist
        }
    )
    checks = validator.validate(payload)
    fail_check = next(c for c in checks if c.field_name == "date_of_birth")
    assert fail_check.status == "FAIL"
    assert "Invalid calendar day" in fail_check.message

def test_expired_document_status():
    validator = DateValidator(reference_date=date(2026, 9, 2))
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_expiry": Module1Field(value="2021-05-20") # Expired
        }
    )
    checks = validator.validate(payload)
    exp_check = next(c for c in checks if c.rule_id == "CHRONO_EXPIRATION_STATUS")
    assert exp_check.status == "FAIL"
    assert exp_check.details["is_expired"] is True

def test_chronology_issue_after_expiry():
    validator = DateValidator(reference_date=date(2026, 9, 2))
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_issue": Module1Field(value="2030-01-01"),
            "date_of_expiry": Module1Field(value="2025-01-01") # Expiry before issue
        }
    )
    checks = validator.validate(payload)
    chrono_check = next(c for c in checks if c.rule_id == "CHRONO_ISSUE_BEFORE_EXPIRY")
    assert chrono_check.status == "FAIL"

def test_future_birth_date():
    validator = DateValidator(reference_date=date(2026, 9, 2))
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_birth": Module1Field(value="2035-01-01") # Future DOB
        }
    )
    checks = validator.validate(payload)
    dob_check = next(c for c in checks if c.rule_id == "CHRONO_DOB_BEFORE_ISSUE")
    assert dob_check.status == "FAIL"
    assert "future" in dob_check.message
