"""Watchlist Trigger Tests for Module 7 Integration."""

import pytest
import numpy as np
from module6_database_sync.src.interface import database_sync_service
from src.interface import screening_orchestrator

def test_watchlist_hit_triggers_secondary_inspection():
    # Insert stolen passport into Module 6 store
    database_sync_service.sync_with_server(incoming_delta=[
        {
            "doc_number": "STOLEN888",
            "country_code": "USA",
            "category": "STOLEN_PASSPORT",
            "record_id": "SLTD-TEST-888",
            "reported_date": "2026-02-01",
            "severity": "CRITICAL",
            "officer_instructions": "Flagged as stolen."
        }
    ])

    m1_stolen = {
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "STOLEN888", "confidence": 0.95},
            "issuing_country": {"value": "USA", "confidence": 0.99},
            "date_of_birth": {"value": "1990-01-01", "confidence": 0.99},
            "date_of_expiry": {"value": "2030-01-01", "confidence": 0.99}
        },
        "mrz": {
            "raw_text": "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\nSTOLEN8884USA9001016M3001012<<<<<<<<<<<<<<<8",
            "confidence": 0.96
        }
    }

    doc_arr = np.ones((200, 200, 3), dtype=np.uint8) * 230
    res = screening_orchestrator.process_screening(
        document_image=doc_arr,
        extracted_fields_override=m1_stolen
    )

    assert res["is_flagged_on_watchlist"] is True
    assert res["recommended_action"] == "SECONDARY_INSPECTION_RECOMMENDED"
    assert res["risk_index"] >= 0.90
