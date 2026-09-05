"""Unit tests for OCRNormalizer in Module 2 Stage 3."""

import pytest
from src.normalizers.ocr_normalizer import OCRNormalizer

@pytest.fixture
def normalizer():
    return OCRNormalizer()

def test_date_separator_normalization_slash(normalizer):
    rec = normalizer.normalize_field("date_of_birth", "1990/05/21")
    assert rec.normalized_value == "1990-05-21"
    assert "STANDARDIZE_DATE_SEPARATORS_ISO8601" in rec.transformations
    assert not rec.ambiguity_detected

def test_date_separator_normalization_dot(normalizer):
    rec = normalizer.normalize_field("date_of_expiry", "2030.12.31")
    assert rec.normalized_value == "2030-12-31"
    assert "STANDARDIZE_DATE_SEPARATORS_ISO8601" in rec.transformations

def test_date_separator_normalization_space(normalizer):
    rec = normalizer.normalize_field("issue_date", "2020 01 15")
    assert rec.normalized_value == "2020-01-15"
    assert "STANDARDIZE_DATE_SEPARATORS_ISO8601" in rec.transformations

def test_numeric_date_character_confusion_repair(normalizer):
    rec = normalizer.normalize_field("date_of_birth", "2O25-O8-12") # 'O' instead of '0'
    assert rec.normalized_value == "2025-08-12"
    assert rec.ambiguity_detected is True
    assert "DISAMBIGUATE_NUMERIC_DATE_CHARS" in rec.transformations[0]

def test_identifier_whitespace_removal(normalizer):
    rec = normalizer.normalize_field("passport_number", "P 1234 5678 ")
    assert rec.normalized_value == "P12345678"
    assert "STRIP_INTERNAL_WHITESPACE" in rec.transformations

def test_country_code_uppercase(normalizer):
    rec = normalizer.normalize_field("nationality", " usa ")
    assert rec.normalized_value == "USA"
    assert "UPPERCASE_COUNTRY_CODE" in rec.transformations

def test_unicode_control_characters_removal(normalizer):
    # Include zero-width space and invisible control chars
    dirty_text = "JOHN\u200B SMITH\x00"
    rec = normalizer.normalize_field("full_name", dirty_text)
    assert rec.normalized_value == "JOHN SMITH"
    assert "STRIP_CONTROL_CHARACTERS" in rec.transformations

def test_name_accents_preserved(normalizer):
    rec = normalizer.normalize_field("full_name", "José María Aznar-López")
    assert rec.normalized_value == "JOSÉ MARÍA AZNAR-LÓPEZ"

def test_raw_value_preserved_in_payload_normalization(normalizer):
    fields = {
        "passport_number": type("FieldObj", (), {"value": " p 998877 ", "raw_value": "", "corrections": []})()
    }
    res = normalizer.normalize_payload_fields(fields)
    assert fields["passport_number"].value == "P998877"
    assert fields["passport_number"].raw_value == " p 998877 "
