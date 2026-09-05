"""Unit Tests for ConsistencyValidator and Cross-Field Matching."""

from src.validators.consistency_validator import ConsistencyValidator
from src.schemas.input_schema import Module1InputPayload, Module1Field, Module1MRZ, Module1DocumentType

def test_visual_mrz_consistency_match():
    validator = ConsistencyValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "passport_number": Module1Field(value="P12345678"),
            "nationality": Module1Field(value="USA"),
            "date_of_expiry": Module1Field(value="2030-08-25")
        },
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=True
        )
    )
    checks = validator.validate(payload)
    assert any(c.rule_id == "CROSS_VISUAL_MRZ_DOC_NUMBER" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "CROSS_VISUAL_MRZ_NATIONALITY" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "CROSS_VISUAL_MRZ_EXPIRY" and c.status == "PASS" for c in checks)

def test_visual_mrz_number_mismatch():
    validator = ConsistencyValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        fields={
            "passport_number": Module1Field(value="P99999999"), # Discrepant from MRZ
            "nationality": Module1Field(value="USA"),
            "date_of_expiry": Module1Field(value="2030-08-25")
        },
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=True
        )
    )
    checks = validator.validate(payload)
    mismatch_chk = next(c for c in checks if c.rule_id == "CROSS_VISUAL_MRZ_DOC_NUMBER")
    assert mismatch_chk.status == "FAIL"
    assert "conflicts" in mismatch_chk.message

def test_injected_conflict_passthrough():
    validator = ConsistencyValidator()
    payload = Module1InputPayload(
        status="REVIEW_REQUIRED",
        document_type=Module1DocumentType(value="passport"),
        fields={},
        consistency={
            "status": "CONFLICT",
            "conflicts": [
                {
                    "field": "date_of_birth",
                    "status": "CONFLICT",
                    "visual_value": "1985-04-12",
                    "mrz_value": "1986-04-12"
                }
            ]
        }
    )
    checks = validator.validate(payload)
    conflict_chk = next(c for c in checks if c.rule_id == "CROSS_VISUAL_MRZ_DATE_OF_BIRTH")
    assert conflict_chk.status == "FAIL"
