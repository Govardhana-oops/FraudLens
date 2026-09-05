"""Expanded MRZ Standards Test Suite for Module 2 Stage 3 (TD1, TD2, TD3, MRV-A, MRV-B)."""

import pytest
from src.interface import document_validator

# 1. TD2 Format ($2 \times 36$ characters)
def test_valid_td2_mrz():
    # TD2 2-line MRZ (36 characters per line)
    # Line 1: I<UTOD231458907<<<<<<<<<<<<<<<<<<
    # Line 2: D231458907UTO7408122F1204159<<<<<<<6
    # Let's verify:
    # doc num D23145890, cd = 7
    # dob 740812, cd = 2
    # exp 120415, cd = 9
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "national_id", "confidence": 0.95},
        "fields": {
            "id_number": {"value": "D23145890", "status": "VALID"},
            "full_name": {"value": "ERIKSSON ANNA", "status": "VALID"},
            "date_of_birth": {"value": "1974-08-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-04-15", "status": "VALID"}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD2",
            "lines": [
                "I<UTOD23145890<<<<<<<<<<<<<<<<<<<<<<",
                "D231458907UTO7408122F3004157<<<<<<<8"
            ],
            "checksum_valid": True
        },
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    # Checks that TD2 geometry passed
    geom_chk = next(c for c in res["checks"] if c["rule_id"] == "MRZ_LINE_GEOMETRY")
    assert geom_chk["status"] == "PASS"

def test_corrupted_td2_mrz_checksum():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "national_id", "confidence": 0.95},
        "fields": {
            "id_number": {"value": "D23145890", "status": "VALID"},
            "full_name": {"value": "ERIKSSON ANNA", "status": "VALID"},
            "date_of_birth": {"value": "1974-08-12", "status": "VALID"}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD2",
            "lines": [
                "I<UTOD23145890<<<<<<<<<<<<<<<<<<<<<<",
                "D231458900UTO7408122F3004159<<<<<<<8" # Wrong check digit (0 instead of 7)
            ],
            "checksum_valid": False
        },
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] == "INVALID"
    doc_chk = next(c for c in res["checks"] if c["rule_id"] == "MRZ_DOC_NUMBER_CHECKSUM")
    assert doc_chk["status"] == "FAIL"

# 2. MRV-B Format ($2 \times 36$ characters)
def test_valid_mrv_b_mrz():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "visa", "confidence": 0.95},
        "fields": {
            "visa_number": {"value": "V12345678", "status": "VALID"},
            "date_of_expiry": {"value": "2028-09-20", "status": "VALID"}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "MRV-B",
            "lines": [
                "V<UTOMULLER<<HANS<<<<<<<<<<<<<<<<<<<",
                "V123456789UTO8001014M2809205<<<<<<<<"
            ],
            "checksum_valid": True
        },
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    geom_chk = next(c for c in res["checks"] if c["rule_id"] == "MRZ_LINE_GEOMETRY")
    assert geom_chk["status"] == "PASS"
