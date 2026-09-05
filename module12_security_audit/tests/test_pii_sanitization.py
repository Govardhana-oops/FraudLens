"""Biometric PII Sanitization and Redaction Verification for Module 12."""

import pytest
import numpy as np
from module7_integration_engine.src.interface import screening_orchestrator
from module12_security_audit.src.auditor import SecurityAuditor

def test_no_raw_biometric_vectors_in_dossier():
    doc_img = np.ones((100, 100, 3), dtype=np.uint8) * 200
    res = screening_orchestrator.process_screening(doc_img)

    audit_res = SecurityAuditor.audit_dossier_privacy(res)
    assert audit_res["privacy_compliant"] is True
    assert len(audit_res["violations"]) == 0

    # Ensure 128D raw numpy feature embeddings are not dumped in the json payload
    dossier_str = str(res)
    assert "raw_biometric_vector" not in dossier_str
    assert "secret_key" not in dossier_str
