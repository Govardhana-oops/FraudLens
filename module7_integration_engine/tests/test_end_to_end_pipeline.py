"""End-to-End Pipeline Verification for Module 7."""

import pytest
import numpy as np
from src.interface import screening_orchestrator

def test_end_to_end_invalid_document_routing():
    # Pass invalid calendar date in M1 override
    invalid_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "P99887766", "confidence": 0.95},
            "date_of_birth": {"value": "2023-02-29", "confidence": 0.99}, # Impossible leap year
            "date_of_expiry": {"value": "2030-01-01", "confidence": 0.99},
            "issuing_country": {"value": "USA", "confidence": 0.99}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P998877664USA2302296M3001012<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": False,
            "checks": {"composite": False}
        },
        "visual_mrz_conflicts": []
    }

    doc_arr = np.ones((200, 200, 3), dtype=np.uint8) * 230
    res = screening_orchestrator.process_screening(
        document_image=doc_arr,
        extracted_fields_override=invalid_m1
    )

    assert res["recommended_action"] in ["SECONDARY_INSPECTION_RECOMMENDED", "TECHNICAL_REVIEW_REQUIRED"]
    assert res["modules_telemetry"]["module2_document_validation"]["status"] == "INVALID"
    assert res["risk_index"] > 0.25
