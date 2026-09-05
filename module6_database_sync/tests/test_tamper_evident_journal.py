"""Tamper-Evident SHA-256 Hash Chaining Tests."""

import pytest
from src.security.hash_integrity import TamperEvidentHasher

def test_audit_hash_chaining_and_tamper_detection(test_sync_service):
    # Log 3 sequential inspection events
    e1 = test_sync_service.log_inspection("CLEAR", 0.05, "DOC001")
    e2 = test_sync_service.log_inspection("CLEAR", 0.10, "DOC002")
    e3 = test_sync_service.log_inspection("SECONDARY_INSPECTION_RECOMMENDED", 0.85, "DOC003")

    assert e2["prev_hash"] == e1["entry_hash"]
    assert e3["prev_hash"] == e2["entry_hash"]

    # Verify cryptographic signature of e2
    payload_e2 = {
        "log_id": e2["log_id"],
        "timestamp": e2["timestamp"],
        "officer_id": e2["officer_id"],
        "checkpoint_id": e2["checkpoint_id"],
        "doc_number": e2["doc_number"],
        "recommended_action": e2["recommended_action"],
        "risk_index": e2["risk_index"]
    }
    assert TamperEvidentHasher.verify_chain_link(e1["entry_hash"], payload_e2, e2["entry_hash"]) is True

    # If payload is maliciously altered, signature verification fails
    tampered_payload = payload_e2.copy()
    tampered_payload["recommended_action"] = "TAMPERED_ACTION"
    assert TamperEvidentHasher.verify_chain_link(e1["entry_hash"], tampered_payload, e2["entry_hash"]) is False
