"""Unit & Integration Tests for Document Understanding Pipeline (Stage 5).

Tests:
1. Normal Cases: Clear Passport, Visa, Driver's License, National ID, Residence Permit
2. Difficult Cases: Multiline Address, Textual Month Dates, OCR Spacing, Character Disambiguation
3. Safety & Robustness Cases: Unsupported Doc Type (UNKNOWN), Conflicting Fields (CONFLICT), Malformed Inputs
"""

import pytest
from src.extraction.pipeline import DocumentUnderstandingPipeline
from src.extraction.normalizer import FieldNormalizer
from src.extraction.validator import FieldValidator
from src.extraction.schema import ExtractedField

@pytest.fixture
def pipeline():
    return DocumentUnderstandingPipeline()

@pytest.fixture
def normalizer():
    return FieldNormalizer()

@pytest.fixture
def validator():
    return FieldValidator()

# --------------------------------------------------------------------------
# 1. NORMAL CASES
# --------------------------------------------------------------------------

def test_passport_understanding_pipeline(pipeline):
    sample_text = """
    PASSPORT / PASSEPORT
    COUNTRY CODE: UTO
    PASSPORT NO: P12345678
    SURNAME: SMITH
    GIVEN NAMES: JOHN MICHAEL
    NATIONALITY: UTO
    DATE OF BIRTH: 1985-04-12
    SEX: M
    DATE OF EXPIRY: 2030-08-25
    P<UTOSMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<
    P123456789UTO8504124M3008258<<<<<<<<<<<<<<<8
    """
    res = pipeline.process(sample_text)
    assert res.document_type == "passport"
    assert res.document_type_confidence >= 0.80
    assert res.fields["passport_number"].value == "P12345678"
    assert res.fields["full_name"].value == "JOHN MICHAEL SMITH"
    assert res.fields["date_of_birth"].value == "1985-04-12"
    assert res.fields["nationality"].value == "UTO"
    assert res.mrz_validation is not None
    assert res.mrz_validation.all_checksums_pass is True
    assert res.status == "SUCCESS"
    assert res.review_required is False

def test_visa_understanding_pipeline(pipeline):
    sample_text = """
    TRAVEL VISA
    VISA NO: V9876543
    BEARER: JANE DOE
    PASSPORT NO: P87654321
    VALID FROM: 2024-01-01
    VALID UNTIL: 2024-12-31
    ENTRIES: MULTIPLE
    V<UTODOE<<JANE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    V9876543<7UTO8504128F2412314<<<<<<<<<<<<<<00
    """
    res = pipeline.process(sample_text)
    assert res.document_type == "visa"
    assert res.fields["visa_number"].value == "V9876543"
    assert res.fields["full_name"].value == "JANE DOE"
    assert res.fields["issue_date"].value == "2024-01-01"
    assert res.fields["expiry_date"].value == "2024-12-31"

def test_driver_license_multiline_understanding(pipeline):
    sample_text = """
    DRIVER LICENSE
    DL NO: DL-90123456
    NAME: ROBERT BRUCE
    ADDR: 742 EVERGREEN TERRACE, SPRINGFIELD
    DOB: 1978-11-23
    SEX: M
    ISS: 2020-05-15
    EXP: 2028-05-15
    CLASS: C COMMERCIAL
    """
    res = pipeline.process(sample_text)
    assert res.document_type == "driver_license"
    assert res.fields["license_number"].value == "DL-90123456"
    assert res.fields["full_name"].value == "ROBERT BRUCE"
    assert "EVERGREEN TERRACE" in res.fields["address"].value
    assert res.fields["date_of_birth"].value == "1978-11-23"
    assert res.fields["vehicle_class"].value == "C COMMERCIAL"

def test_permit_understanding(pipeline):
    sample_text = """
    RESIDENCE PERMIT
    PERMIT NO: RP-55443322
    HOLDER: ALICE WONDERLAND
    CATEGORY: HIGHLY SKILLED MIGRANT
    VALID UNTIL: 2027-08-30
    EMPLOYER: TECH CORP GLOBAL
    """
    res = pipeline.process(sample_text)
    assert res.document_type == "permit"
    assert res.fields["permit_number"].value == "RP-55443322"
    assert res.fields["full_name"].value == "ALICE WONDERLAND"
    assert res.fields["permit_category"].value == "HIGHLY SKILLED MIGRANT"
    assert res.fields["sponsor"].value == "TECH CORP GLOBAL"

# --------------------------------------------------------------------------
# 2. DIFFICULT & EDGE CASES
# --------------------------------------------------------------------------

def test_normalizer_date_variants(normalizer):
    d1, _ = normalizer.normalize_date("20 MAY 1999")
    assert d1 == "1999-05-20"
    d2, _ = normalizer.normalize_date("15/08/2025")
    assert d2 == "2025-08-15"
    d3, _ = normalizer.normalize_date("850412")
    assert d3 == "1985-04-12"

def test_passport_character_disambiguation(normalizer):
    norm_doc, corr = normalizer.disambiguate_document_number("P1234O67", doc_type="passport")
    assert norm_doc == "P1234067"
    assert len(corr) == 1
    assert corr[0]["from"] == "O"
    assert corr[0]["to"] == "0"

# --------------------------------------------------------------------------
# 3. SAFETY & ROBUSTNESS CASES
# --------------------------------------------------------------------------

def test_unknown_document_safety(pipeline):
    unsupported_text = "RANDOM INVOICE TOTAL $500 PAID IN FULL FOR SERVICES RENDERED"
    res = pipeline.process(unsupported_text)
    assert res.document_type == "unknown_document"
    assert res.status == "UNKNOWN"
    assert res.review_required is True

def test_cross_field_conflict_detection(pipeline):
    conflicting_text = """
    PASSPORT / PASSEPORT
    PASSPORT NO: P12345678
    SURNAME: SMITH
    GIVEN NAMES: JOHN
    DATE OF BIRTH: 1985-04-12
    NATIONALITY: UTO
    P<UTOSMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    P123456784UTO8604128M3008251<<<<<<<<<<<<<<02
    """
    res = pipeline.process(conflicting_text)
    assert len(res.cross_field_conflicts) > 0
    dob_conflict = next((c for c in res.cross_field_conflicts if c.field == "date_of_birth"), None)
    assert dob_conflict is not None
    assert dob_conflict.status == "CONFLICT"
    assert dob_conflict.visual_value == "1985-04-12"
    assert dob_conflict.mrz_value == "1986-04-12"
    assert res.review_required is True

def test_chronological_anomaly_warning(validator):
    fields = {
        "date_of_birth": ExtractedField(value="2020-01-01", raw_value="2020-01-01", confidence=1.0),
        "date_of_issue": ExtractedField(value="2015-01-01", raw_value="2015-01-01", confidence=1.0),
        "date_of_expiry": ExtractedField(value="2025-01-01", raw_value="2025-01-01", confidence=1.0),
    }
    warnings = validator.validate_chronology(fields)
    assert len(warnings) > 0
    assert any("DOB" in w and "Issue Date" in w for w in warnings)
