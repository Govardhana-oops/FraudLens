"""Unit Tests for Structured Document Field Extraction."""

import pytest
from src.extraction.field_extractor import FieldExtractor

def test_extract_driver_license():
    extractor = FieldExtractor()
    raw_text = """
    STATE OF UTOPIA — DRIVER LICENSE
    DL NO: DL-P91823746
    NAME: SMITH, JOHN MICHAEL
    ADDR: 1234 MAIN ST, NEW HAVEN, UTO
    DOB: 1985-04-12
    SEX: M
    ISS: 2020-04-12
    EXP: 2030-04-12
    CLASS: CLASS C (STANDARD PASSENGER)
    """
    res = extractor.extract(raw_text)
    assert res.document_type == "driver_license"
    assert res.status == "SUCCESS"
    assert res.fields["license_number"].value == "DL-P91823746"
    assert res.fields["full_name"].value == "SMITH JOHN MICHAEL"
    assert res.fields["date_of_birth"].value == "1985-04-12"
    assert res.fields["vehicle_class"].value == "CLASS C (STANDARD PASSENGER)"

def test_extract_permit():
    extractor = FieldExtractor()
    raw_text = """
    RESIDENCE & WORK PERMIT — UTOPIA
    PERMIT NO: RP-P91823746
    HOLDER: JOHNSON, EMMA
    CATEGORY: SPECIAL SKILLS TALENT
    VALID UNTIL: 2029-08-15
    EMPLOYER: XANADU TECH CORP
    """
    res = extractor.extract(raw_text)
    assert res.document_type == "permit"
    assert res.status == "SUCCESS"
    assert res.fields["permit_number"].value == "RP-P91823746"
    assert res.fields["full_name"].value == "JOHNSON EMMA"
    assert res.fields["permit_category"].value == "SPECIAL SKILLS TALENT"

def test_extract_passport_viz_and_mrz():
    extractor = FieldExtractor()
    raw_text = """
    PASSPORT / PASSEPORT — UTOPIA
    TYPE: P CODE: UTO PASSPORT NO: P91823746
    SURNAME / NOM:
    SMITH
    GIVEN NAMES / PRENOMS:
    JOHN MICHAEL
    NATIONALITY / NATIONALITE:
    UTOPIA (UTO)
    DATE OF BIRTH:
    1985-04-12
    SEX:
    M
    P<UTOSMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<
    P918237464UTO8504128M3004121<<<<<<<<<<<<<<02
    """
    res = extractor.extract(raw_text)
    assert res.document_type == "passport"
    assert res.status == "SUCCESS"
    assert res.fields["passport_number"].value == "P91823746"
    assert res.fields["surname"].value == "SMITH"
    assert res.fields["given_names"].value == "JOHN MICHAEL"
    assert res.mrz_validation is not None
    assert res.mrz_validation.mrz_format == "TD3"

def test_extract_visa():
    extractor = FieldExtractor()
    raw_text = """
    TRAVEL VISA — UTOPIA
    VISA NO: V82736451
    BEARER: WILLIAMS, DAVID
    PASSPORT NO: P91823746
    VALID FROM: 2022-01-10
    VALID UNTIL: 2027-01-10
    ENTRIES: MULTIPLE
    VN<UTOWILLIAMS<<DAVID<<<<<<<<<<<<<<<<<<<<<<<
    V827364514UTO8504128M2701101<<<<<<<<<<<<<<<<
    """
    res = extractor.extract(raw_text)
    assert res.document_type == "visa"
    assert res.status == "SUCCESS"
    assert res.fields["visa_number"].value == "V82736451"
    assert res.fields["full_name"].value == "WILLIAMS DAVID"

def test_extract_national_id():
    extractor = FieldExtractor()
    raw_text = """
    NATIONAL IDENTITY CARD — UTOPIA
    ID NO: ID-P91823746
    NAME: BROWN, SARAH
    DOB: 1992-06-15
    CITIZENSHIP: UTO
    EXPIRY: 2032-06-15
    I<UTO91823746<<<<<<<<<<<<<<<<<
    9206158F3206151UTO<<<<<<<<<<<<
    BROWN<<SARAH<<<<<<<<<<<<<<<<<<
    """
    res = extractor.extract(raw_text)
    assert res.document_type == "national_id"
    assert res.status == "SUCCESS"
    assert res.fields["id_number"].value == "ID-P91823746"
    assert res.fields["full_name"].value == "SARAH BROWN"
