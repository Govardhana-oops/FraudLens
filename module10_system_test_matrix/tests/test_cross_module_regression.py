"""Cross-Module Permutation & Regression Matrix for Module 10."""

import pytest
import numpy as np
from module7_integration_engine.src.interface import screening_orchestrator

@pytest.mark.parametrize("m2_status", ["VALID", "INVALID", "EXPIRED", "REVIEW_REQUIRED"])
def test_cross_module_validation_status_permutations(m2_status):
    mock_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "P77889900", "confidence": 0.95},
            "date_of_birth": {"value": "1990-01-01" if m2_status != "INVALID" else "2023-02-29", "confidence": 0.99},
            "date_of_expiry": {"value": "2030-01-01" if m2_status != "EXPIRED" else "2018-01-01", "confidence": 0.99},
            "issuing_country": {"value": "USA", "confidence": 0.99}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P778899004USA9001016M3001012<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": (m2_status != "INVALID"),
            "checks": {"composite": (m2_status != "INVALID")}
        },
        "visual_mrz_conflicts": []
    }

    doc_img = np.ones((200, 200, 3), dtype=np.uint8) * 230
    res = screening_orchestrator.process_screening(doc_img, extracted_fields_override=mock_m1)

    assert 0.0 <= res["risk_index"] <= 1.0
    assert res["recommended_action"] in [
        "CLEAR", "STANDARD_INSPECTION", "SECONDARY_INSPECTION_RECOMMENDED",
        "TECHNICAL_REVIEW_REQUIRED", "RECAPTURE_REQUIRED"
    ]
