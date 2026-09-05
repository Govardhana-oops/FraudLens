"""Unit Tests for ICAO Doc 9303 MRZ Parsing & Checksums."""

import pytest
from src.ocr.mrz_parser import MRZParser, calculate_mrz_checksum, verify_check_digit

def test_mrz_checksum_calculation():
    # Test known passport number checksum
    doc_num = "P12345678"
    chk = calculate_mrz_checksum(doc_num)
    assert isinstance(chk, int)
    assert 0 <= chk <= 9
    assert verify_check_digit(doc_num, str(chk)) is True
    assert verify_check_digit(doc_num, "9" if chk != 9 else "0") is False

def test_td3_passport_mrz_parsing():
    parser = MRZParser()
    mrz_text = """
    PASSPORT / PASSEPORT
    P<UTOSMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<
    P123456784UTO8504128M3008251<<<<<<<<<<<<<<02
    """
    fields, validation = parser.parse(mrz_text)
    assert validation is not None
    assert validation.mrz_format == "TD3"
    assert "passport_number" in fields
    assert fields["passport_number"].value == "P12345678"
    assert fields["surname"].value == "SMITH"
    assert fields["given_names"].value == "JOHN MICHAEL"
    assert fields["nationality"].value == "UTO"
    assert fields["date_of_birth"].value == "850412"
    assert fields["gender"].value == "M"

def test_td1_national_id_mrz_parsing():
    parser = MRZParser()
    mrz_text = """
    I<UTO123456789<<<<<<<<<<<<<<<<
    8504128M3008251UTO<<<<<<<<<<<<
    SMITH<<JOHN<MICHAEL<<<<<<<<<<<
    """
    fields, validation = parser.parse(mrz_text)
    assert validation is not None
    assert validation.mrz_format == "TD1"
    assert fields["id_number"].value == "123456789"
    assert fields["surname"].value == "SMITH"
    assert fields["given_names"].value == "JOHN MICHAEL"
