"""Real-World Border Control Scenarios Test Matrix for Module 10."""

import pytest
import numpy as np
import cv2
from module6_database_sync.src.interface import database_sync_service
from module7_integration_engine.src.interface import screening_orchestrator
from module10_system_test_matrix.src.generators.scenario_generator import ScenarioGenerator

def test_scenario_01_genuine_authentic_passport():
    valid_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "P12345678", "confidence": 0.95},
            "full_name": {"value": "JOHN DOE", "confidence": 0.99},
            "date_of_birth": {"value": "1990-05-15", "confidence": 0.99},
            "date_of_expiry": {"value": "2030-05-14", "confidence": 0.99},
            "issuing_country": {"value": "USA", "confidence": 0.99}
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
        "visual_mrz_conflicts": []
    }
    doc_img = ScenarioGenerator.create_synthetic_passport_image("P12345678", "DOE JOHN")
    res = screening_orchestrator.process_screening(doc_img, extracted_fields_override=valid_m1)
    assert res["recommended_action"] in ["CLEAR", "STANDARD_INSPECTION", "TECHNICAL_REVIEW_REQUIRED"]
    assert res["risk_index"] < 0.35
    assert res["is_flagged_on_watchlist"] is False

def test_scenario_02_expired_document_clearance():
    expired_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "P22334455", "confidence": 0.95},
            "full_name": {"value": "ALICE SMITH", "confidence": 0.99},
            "date_of_birth": {"value": "1980-01-01", "confidence": 0.99},
            "date_of_expiry": {"value": "2020-01-01", "confidence": 0.99}, # Expired in 2020
            "issuing_country": {"value": "USA", "confidence": 0.99}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USASMIT<<ALICE<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P223344555USA8001014M2001012<<<<<<<<<<<<<<<3"
            ],
            "checksum_valid": True,
            "checks": {"composite": True}
        },
        "visual_mrz_conflicts": []
    }
    doc_img = ScenarioGenerator.create_synthetic_passport_image("P22334455")
    res = screening_orchestrator.process_screening(doc_img, extracted_fields_override=expired_m1)
    assert res["recommended_action"] in ["STANDARD_INSPECTION", "TECHNICAL_REVIEW_REQUIRED", "SECONDARY_INSPECTION_RECOMMENDED"]
    assert res["modules_telemetry"]["module2_document_validation"]["status"] in ["EXPIRED", "INVALID"]

def test_scenario_03_photo_spliced_tampering():
    doc_img = ScenarioGenerator.create_synthetic_passport_image("P33445566")
    noise_block = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    doc_img[80:180, 80:180] = noise_block

    res = screening_orchestrator.process_screening(doc_img)
    assert res["recommended_action"] in ["SECONDARY_INSPECTION_RECOMMENDED", "TECHNICAL_REVIEW_REQUIRED"]
    assert res["risk_index"] > 0.20

def test_scenario_04_stolen_sltd_watchlist_hit():
    database_sync_service.sync_with_server(incoming_delta=[
        {
            "doc_number": "SLTD9999",
            "country_code": "USA",
            "category": "STOLEN_PASSPORT",
            "record_id": "SLTD-E2E-9999",
            "reported_date": "2026-03-01",
            "severity": "CRITICAL",
            "officer_instructions": "Stop passenger."
        }
    ])

    stolen_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "SLTD9999", "confidence": 0.95},
            "full_name": {"value": "JOHN DOE", "confidence": 0.99},
            "issuing_country": {"value": "USA", "confidence": 0.99},
            "date_of_birth": {"value": "1990-01-01", "confidence": 0.99},
            "date_of_expiry": {"value": "2030-01-01", "confidence": 0.99}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "SLTD99994USA9001016M3001012<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": True,
            "checks": {"composite": True}
        },
        "visual_mrz_conflicts": []
    }
    doc_img = ScenarioGenerator.create_synthetic_passport_image("SLTD9999")
    res = screening_orchestrator.process_screening(doc_img, extracted_fields_override=stolen_m1)

    assert res["is_flagged_on_watchlist"] is True
    assert res["recommended_action"] == "SECONDARY_INSPECTION_RECOMMENDED"
    assert res["risk_index"] >= 0.90
