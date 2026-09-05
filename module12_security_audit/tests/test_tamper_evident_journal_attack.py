"""Tamper-Evident Attack Simulation on Audit Journal for Module 12."""

import pytest
import sqlite3
from module6_database_sync.src.interface import database_sync_service
from module6_database_sync.src.security.hash_integrity import TamperEvidentHasher

def test_tamper_evident_hash_chain_attack_detection():
    # 1. Create a legitimate audit log entry
    legit_entry = database_sync_service.log_inspection(
        recommended_action="CLEAR",
        risk_index=0.05,
        doc_number="AUDIT_TEST_01"
    )

    entries = database_sync_service.store.get_unsynced_audit_entries(limit=10)
    assert len(entries) > 0

    # 2. Simulate attacker tampering with risk_index in SQLite
    last_entry = entries[-1]
    tampered_payload = {
        "log_id": last_entry.log_id,
        "timestamp": last_entry.timestamp,
        "officer_id": last_entry.officer_id,
        "checkpoint_id": last_entry.checkpoint_id,
        "doc_number": last_entry.doc_number,
        "recommended_action": "SECONDARY_INSPECTION_RECOMMENDED", # Tampered action!
        "risk_index": 0.99                                       # Tampered risk!
    }

    # 3. Verify that the cryptographic hash verification detects the mismatch
    is_valid = TamperEvidentHasher.verify_chain_link(
        last_entry.prev_hash,
        tampered_payload,
        last_entry.entry_hash
    )
    assert is_valid is False, "Cryptographic chain must detect tampered payload!"
