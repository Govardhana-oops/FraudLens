"""Unit Tests for Document-Specific Validators (Passport, Visa, DL, ID, Permit)."""

from src.validators.passport_validator import PassportValidator
from src.validators.visa_validator import VisaValidator
from src.validators.license_validator import LicenseValidator
from src.validators.national_id_validator import NationalIDValidator
from src.validators.permit_validator import PermitValidator
from src.schemas.input_schema import Module1InputPayload, Module1Field, Module1DocumentType

def test_passport_validator_success():
    v = PassportValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "passport_number": Module1Field(value="P12345678"),
            "full_name": Module1Field(value="JOHN SMITH"),
            "nationality": Module1Field(value="USA"),
            "date_of_birth": Module1Field(value="1985-04-12"),
            "date_of_expiry": Module1Field(value="2030-08-25"),
            "gender": Module1Field(value="M")
        }
    )
    checks = v.validate(payload)
    assert all(c.status == "PASS" for c in checks)

def test_passport_missing_mandatory_field():
    v = PassportValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "full_name": Module1Field(value="JOHN SMITH"),
            "nationality": Module1Field(value="USA")
            # passport_number and date_of_expiry missing
        }
    )
    checks = v.validate(payload)
    missing_chk = next(c for c in checks if c.field_name == "passport_number")
    assert missing_chk.status == "UNKNOWN"

def test_license_minimum_driving_age():
    v = LicenseValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="driver_license"),
        fields={
            "license_number": Module1Field(value="DL-12345678"),
            "full_name": Module1Field(value="TEEN DRIVER"),
            "date_of_birth": Module1Field(value="2012-01-01"),
            "issue_date": Module1Field(value="2024-01-01"), # Age at issue = 12 years (Under 16)
            "expiry_date": Module1Field(value="2029-01-01")
        }
    )
    checks = v.validate(payload)
    age_chk = next(c for c in checks if c.rule_id == "DOMAIN_DL_MINIMUM_AGE")
    assert age_chk.status == "FAIL"
    assert "below minimum driving threshold" in age_chk.message

def test_permit_validator_category():
    v = PermitValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="permit"),
        fields={
            "permit_number": Module1Field(value="PRM-98765432"),
            "permit_category": Module1Field(value="WORK AUTHORIZATION"),
            "valid_until": Module1Field(value="2028-10-10"),
            "sponsor": Module1Field(value="ACME CORP")
        }
    )
    checks = v.validate(payload)
    cat_chk = next(c for c in checks if c.rule_id == "DOMAIN_PERMIT_CATEGORY_VALIDITY")
    assert cat_chk.status == "PASS"
