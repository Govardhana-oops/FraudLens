"""Unit Tests for Systematic Cross-Field & Visual-MRZ Consistency Matrix."""

import pytest
from datetime import date
from src.validators.date_validator import DateValidator
from src.validators.consistency_validator import ConsistencyValidator
from src.schemas.input_schema import Module1InputPayload, Module1Field, Module1MRZ, Module1DocumentType

@pytest.fixture
def date_val():
    return DateValidator(reference_date=date(2026, 9, 2))

@pytest.fixture
def cons_val():
    return ConsistencyValidator()

# 1. DOB < Issue Date -> PASS
def test_dob_before_issue_pass(date_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_birth": Module1Field(value="1990-01-01"),
            "date_of_issue": Module1Field(value="2020-01-01"),
            "date_of_expiry": Module1Field(value="2030-01-01")
        }
    )
    checks = date_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CHRONO_DOB_BEFORE_ISSUE")
    assert chk.status == "PASS"

# 2. DOB >= Issue Date -> FAIL
def test_dob_after_issue_fail(date_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_birth": Module1Field(value="2025-01-01"),
            "date_of_issue": Module1Field(value="2020-01-01")
        }
    )
    checks = date_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CHRONO_DOB_BEFORE_ISSUE")
    assert chk.status == "FAIL"

# 3. Issue <= Expiry -> PASS
def test_issue_before_expiry_pass(date_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_issue": Module1Field(value="2020-01-01"),
            "date_of_expiry": Module1Field(value="2030-01-01")
        }
    )
    checks = date_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CHRONO_ISSUE_BEFORE_EXPIRY")
    assert chk.status == "PASS"

# 4. Issue > Expiry -> FAIL
def test_issue_after_expiry_fail(date_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "date_of_issue": Module1Field(value="2030-01-01"),
            "date_of_expiry": Module1Field(value="2025-01-01")
        }
    )
    checks = date_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CHRONO_ISSUE_BEFORE_EXPIRY")
    assert chk.status == "FAIL"

# 5. Visual Doc No == MRZ Doc No -> PASS
def test_visual_mrz_doc_num_equal(cons_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={"passport_number": Module1Field(value="P12345678")},
        mrz=Module1MRZ(
            status="VALID", mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=True
        )
    )
    checks = cons_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CROSS_VISUAL_MRZ_DOC_NUMBER")
    assert chk.status == "PASS"

# 6. Visual Doc No != MRZ Doc No -> CONFLICT / FAIL
def test_visual_mrz_doc_num_different(cons_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={"passport_number": Module1Field(value="P99999999")},
        mrz=Module1MRZ(
            status="VALID", mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=True
        )
    )
    checks = cons_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CROSS_VISUAL_MRZ_DOC_NUMBER")
    assert chk.status == "FAIL"

# 7. Visual Expiry == MRZ Expiry -> PASS
def test_visual_mrz_expiry_equal(cons_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={"date_of_expiry": Module1Field(value="2030-08-25")},
        mrz=Module1MRZ(
            status="VALID", mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=True
        )
    )
    checks = cons_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CROSS_VISUAL_MRZ_EXPIRY")
    assert chk.status == "PASS"

# 8. Visual Expiry != MRZ Expiry -> CONFLICT / FAIL
def test_visual_mrz_expiry_different(cons_val):
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={"date_of_expiry": Module1Field(value="2028-01-01")},
        mrz=Module1MRZ(
            status="VALID", mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=True
        )
    )
    checks = cons_val.validate(payload)
    chk = next(c for c in checks if c.rule_id == "CROSS_VISUAL_MRZ_EXPIRY")
    assert chk.status == "FAIL"
