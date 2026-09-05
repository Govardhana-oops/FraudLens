"""Unit Tests for Module 6 Public Interface."""

import pytest
from src.interface import database_sync_service

def test_interface_clean_watchlist_lookup(test_sync_service):
    # Lookup non-existent document
    res = test_sync_service.lookup_watchlist("P99999999", "USA")
    assert res["is_flagged"] is False
    assert res["query_doc_number"] == "P99999999"
    assert res["lookup_latency_ms"] < 10.0

def test_interface_log_inspection(test_sync_service):
    entry = test_sync_service.log_inspection(
        recommended_action="CLEAR",
        risk_index=0.12,
        doc_number="A12345678"
    )
    assert entry["doc_number"] == "A12345678"
    assert len(entry["entry_hash"]) == 64
    assert entry["synced_to_cloud"] is False
