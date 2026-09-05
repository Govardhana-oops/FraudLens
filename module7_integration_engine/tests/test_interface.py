"""Unit Tests for Module 7 Public Interface."""

import pytest
import numpy as np
from src.interface import screening_orchestrator

def test_interface_clean_screening_pass():
    doc_arr = np.ones((200, 200, 3), dtype=np.uint8) * 230
    live_arr = np.ones((200, 200, 3), dtype=np.uint8) * 230

    res = screening_orchestrator.process_screening(
        document_image=doc_arr,
        live_face_image=live_arr,
        officer_id="OFFICER-TEST",
        checkpoint_id="GATE-01"
    )

    assert "screening_id" in res
    assert res["recommended_action"] in ["CLEAR", "STANDARD_INSPECTION", "TECHNICAL_REVIEW_REQUIRED", "RECAPTURE_REQUIRED"]
    assert "module1_ocr" in res["modules_telemetry"]
    assert "module2_document_validation" in res["modules_telemetry"]
    assert "module3_tampering_detection" in res["modules_telemetry"]
    assert "module4_face_verification" in res["modules_telemetry"]
    assert "module5_explainable_evidence" in res["modules_telemetry"]
    assert "module6_database_sync" in res["modules_telemetry"]
    assert len(res["audit_log"]["entry_hash"]) == 64
