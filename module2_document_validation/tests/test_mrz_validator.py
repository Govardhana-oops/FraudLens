"""Unit Tests for MRZValidator and Modulo-10 Checksums across TD1, TD2, TD3, MRV."""

from src.validators.mrz_validator import MRZValidator
from src.schemas.input_schema import Module1InputPayload, Module1MRZ, Module1DocumentType

def test_valid_td3_passport_mrz():
    validator = MRZValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
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
    assert any(c.rule_id == "MRZ_LINE_GEOMETRY" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_DOC_NUMBER_CHECKSUM" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_DOB_CHECKSUM" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_EXPIRY_CHECKSUM" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_COMPOSITE_CHECKSUM" and c.status == "PASS" for c in checks)

def test_valid_td1_national_id_mrz():
    validator = MRZValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="national_id"),
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="TD1",
            lines=[
                "I<USA9906192411<<<<<<<<<<<<<<<",
                "9906194M2912039USA<<<<<<<<<<<6",
                "JOHNSON<<NOAH<<<<<<<<<<<<<<<<<"
            ],
            checksum_valid=True
        )
    )
    checks = validator.validate(payload)
    assert any(c.rule_id == "MRZ_LINE_GEOMETRY" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_DOB_CHECKSUM" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_EXPIRY_CHECKSUM" and c.status == "PASS" for c in checks)

def test_valid_mrv_a_visa_mrz():
    validator = MRZValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="visa"),
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="MRV-A",
            lines=[
                "VN<USAJONES<<EMMA<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "V9876543<1USA9206159F2806158<<<<<<<<<<<<<<<<"
            ],
            checksum_valid=True
        )
    )
    checks = validator.validate(payload)
    assert any(c.rule_id == "MRZ_LINE_GEOMETRY" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_DOC_NUMBER_CHECKSUM" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_DOB_CHECKSUM" and c.status == "PASS" for c in checks)
    assert any(c.rule_id == "MRZ_EXPIRY_CHECKSUM" and c.status == "PASS" for c in checks)

def test_corrupted_doc_number_checksum():
    validator = MRZValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456780USA8504124M3008258<<<<<<<<<<<<<<<8" # Check digit changed to 0 (expected 9)
            ],
            checksum_valid=False
        )
    )
    checks = validator.validate(payload)
    doc_chk = next(c for c in checks if c.rule_id == "MRZ_DOC_NUMBER_CHECKSUM")
    assert doc_chk.status == "FAIL"

def test_multiple_simultaneous_checksum_failures():
    validator = MRZValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
                "P123456780USA8504120M3008250<<<<<<<<<<<<<<<0" # All check digits zeroed out
            ],
            checksum_valid=False
        )
    )
    checks = validator.validate(payload)
    fails = [c for c in checks if c.status == "FAIL" and c.category == "MRZ"]
    assert len(fails) >= 3 # Doc number, DOB, Expiry, Composite

def test_invalid_mrz_line_length():
    validator = MRZValidator()
    payload = Module1InputPayload(
        status="SUCCESS",
        document_type=Module1DocumentType(value="passport"),
        mrz=Module1MRZ(
            status="VALID",
            mrz_format="TD3",
            lines=[
                "P<USASMITH<<JOHN<MICHAEL<<<", # Truncated line (27 chars instead of 44)
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            checksum_valid=False
        )
    )
    checks = validator.validate(payload)
    geom_chk = next(c for c in checks if c.rule_id == "MRZ_LINE_GEOMETRY")
    assert geom_chk.status == "FAIL"
