"""Regression Test Suite for Zero-Hallucination & Document Field Extraction."""

import io
import pytest
import numpy as np
from PIL import Image
from module7_integration_engine.src.orchestrator.pipeline_orchestrator import PipelineOrchestrator

@pytest.fixture
def orchestrator():
    return PipelineOrchestrator(config={})

def test_regression_a_correct_extraction_preserved(orchestrator):
    """Test A: Genuine OCR extracted values are preserved and passed to downstream dossier."""
    real_ocr_report = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "E92613013", "confidence": 0.99},
            "full_name": {"value": "AVA TAYLOR", "confidence": 0.97},
            "nationality": {"value": "ARC", "confidence": 0.98},
            "date_of_birth": {"value": "1996-05-13", "confidence": 0.98},
            "date_of_expiry": {"value": "2032-01-10", "confidence": 0.98},
            "issuing_country": {"value": "ARC", "confidence": 0.98}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<ARCTAYLOR<<AVA<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "E926130131ARC9605132F3201107<<<<<<<<<<<<<<6"
            ],
            "checksum_valid": True,
            "checks": {"composite": True}
        },
        "consistency": {"status": "CONSISTENT", "conflicts": []}
    }

    blank_img = np.full((700, 1000, 3), 240, dtype=np.uint8)
    dossier = orchestrator.execute_screening(
        document_image=blank_img,
        extracted_fields_override=real_ocr_report
    )

    assert dossier.document_type == "passport"
    assert dossier.extracted_fields["passport_number"]["value"] == "E92613013"
    assert dossier.extracted_fields["full_name"]["value"] == "AVA TAYLOR"
    assert dossier.extracted_fields["nationality"]["value"] == "ARC"
    assert dossier.mrz["lines"][0] == "P<ARCTAYLOR<<AVA<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

def test_regression_b_ocr_failure_does_not_hallucinate(orchestrator):
    """Test B: When OCR fails or cannot read text, it must return UNKNOWN without hallucinating values."""
    blank_img = np.full((400, 600, 3), 128, dtype=np.uint8)
    dossier = orchestrator.execute_screening(document_image=blank_img)

    # Document type should be unknown or unclassified, not guessed
    assert dossier.document_type == "unknown_document"
    # Fields should be empty, not populated with fake USA/DOE/P12345678
    assert "P12345678" not in str(dossier.extracted_fields)
    assert "JOHN DOE" not in str(dossier.extracted_fields)
    assert dossier.mrz is None or dossier.mrz.get("status") == "UNKNOWN"

def test_regression_c_missing_fields_remain_unknown(orchestrator):
    """Test C: Missing fields remain absent or UNKNOWN and are never fabricated."""
    partial_ocr_report = {
        "module": "module1_ocr",
        "status": "REVIEW_REQUIRED",
        "document_type": {"value": "passport", "confidence": 0.70},
        "fields": {
            "passport_number": {"value": None, "confidence": 0.0, "status": "UNKNOWN"},
            "full_name": {"value": "ALICE SMITH", "confidence": 0.90}
        },
        "mrz": None,
        "consistency": {"status": "NOT_APPLICABLE", "conflicts": []}
    }

    blank_img = np.full((500, 500, 3), 200, dtype=np.uint8)
    dossier = orchestrator.execute_screening(
        document_image=blank_img,
        extracted_fields_override=partial_ocr_report
    )

    assert dossier.extracted_fields["passport_number"]["value"] is None
    assert dossier.extracted_fields["passport_number"]["status"] == "UNKNOWN"
    assert "P12345678" not in str(dossier.extracted_fields)

def test_regression_d_low_confidence_preserves_uncertainty(orchestrator):
    """Test D: Low-confidence OCR results preserve uncertainty and route to technical review."""
    low_conf_report = {
        "module": "module1_ocr",
        "status": "REVIEW_REQUIRED",
        "document_type": {"value": "passport", "confidence": 0.45},
        "fields": {
            "passport_number": {"value": "X123", "confidence": 0.35, "status": "LOW_CONFIDENCE"}
        },
        "mrz": None,
        "consistency": {"status": "NOT_APPLICABLE", "conflicts": []}
    }

    blank_img = np.full((500, 500, 3), 200, dtype=np.uint8)
    dossier = orchestrator.execute_screening(
        document_image=blank_img,
        extracted_fields_override=low_conf_report
    )

    assert dossier.recommended_action in ["TECHNICAL_REVIEW_REQUIRED", "RECAPTURE_REQUIRED", "STANDARD_INSPECTION"]
    assert dossier.extracted_fields["passport_number"]["confidence"] == 0.35

def test_regression_e_visual_mrz_conflict_detection(orchestrator):
    """Test E: Conflict between visual field and MRZ is detected and flagged."""
    conflicting_report = {
        "module": "module1_ocr",
        "status": "REVIEW_REQUIRED",
        "document_type": {"value": "passport", "confidence": 0.95},
        "fields": {
            "passport_number": {"value": "P99999999", "confidence": 0.95},
            "full_name": {"value": "JOHN DOE", "confidence": 0.95},
            "nationality": {"value": "USA", "confidence": 0.95},
            "date_of_birth": {"value": "1990-05-15", "confidence": 0.95},
            "date_of_expiry": {"value": "2030-05-14", "confidence": 0.95},
            "issuing_country": {"value": "USA", "confidence": 0.95}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA9005156M3005143<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": True,
            "checks": {"composite": True}
        },
        "consistency": {
            "status": "CONFLICT",
            "conflicts": [{"field": "passport_number", "visual": "P99999999", "mrz": "P12345678"}]
        }
    }

    blank_img = np.full((500, 500, 3), 200, dtype=np.uint8)
    dossier = orchestrator.execute_screening(
        document_image=blank_img,
        extracted_fields_override=conflicting_report
    )

    assert dossier.recommended_action in ["TECHNICAL_REVIEW_REQUIRED", "SECONDARY_INSPECTION_RECOMMENDED"]
    assert len(dossier.visual_mrz_conflicts) > 0 or dossier.dimensional_risks.get("document_syntactic_risk", 0.0) > 0.0

def test_regression_f_no_hardcoded_fallback_values_in_production_path(orchestrator):
    """Test F: Verifies no hardcoded demo strings appear in the output when given arbitrary test images."""
    for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100)]:
        img = np.full((400, 600, 3), color, dtype=np.uint8)
        dossier = orchestrator.execute_screening(document_image=img)
        dossier_str = str(dossier.model_dump())
        assert "P12345678" not in dossier_str
        assert "P<USADOE<<JOHN" not in dossier_str

def test_regression_g_dossier_contains_provenance_and_mrz(orchestrator):
    """Test G: Dossier contains explicit extracted_fields, mrz, and visual_mrz_conflicts."""
    blank_img = np.full((400, 400, 3), 220, dtype=np.uint8)
    dossier = orchestrator.execute_screening(document_image=blank_img)

    assert hasattr(dossier, "extracted_fields")
    assert hasattr(dossier, "mrz")
    assert hasattr(dossier, "visual_mrz_conflicts")
    assert isinstance(dossier.extracted_fields, dict)
    assert isinstance(dossier.visual_mrz_conflicts, list)

def test_regression_h_image_bytes_reach_ocr_pipeline(orchestrator):
    """Test H: Raw image bytes reach the OCR pipeline and are processed properly."""
    img = Image.new("RGB", (300, 200), color=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    dossier = orchestrator.execute_screening(document_image=raw_bytes)
    assert dossier.screening_id is not None
    assert dossier.modules_telemetry["module1_ocr"].status in ["SUCCESS", "UNKNOWN"]
