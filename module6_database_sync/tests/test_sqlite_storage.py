"""Tests for SQLite Storage and Watchlist Upsert."""

import pytest
from src.schemas.database_models import WatchlistRecord, WatchlistMatchSeverity

def test_upsert_and_fast_lookup(test_sync_service):
    # Upsert a stolen passport
    rec = WatchlistRecord(
        doc_number="STOLEN1234",
        country_code="GBR",
        category="STOLEN_PASSPORT",
        record_id="SLTD-GBR-001",
        reported_date="2026-01-10",
        severity=WatchlistMatchSeverity.CRITICAL,
        officer_instructions="Hold bearer and contact supervisor."
    )
    test_sync_service.store.upsert_watchlist_records([rec])

    # 1. Exact match with country
    res1 = test_sync_service.lookup_watchlist("STOLEN1234", "GBR")
    assert res1["is_flagged"] is True
    assert res1["record"]["record_id"] == "SLTD-GBR-001"
    assert res1["record"]["severity"] == "CRITICAL"

    # 2. Case and whitespace insensitive lookup
    res2 = test_sync_service.lookup_watchlist(" stolen 1234 ")
    assert res2["is_flagged"] is True
    assert res2["record"]["record_id"] == "SLTD-GBR-001"
