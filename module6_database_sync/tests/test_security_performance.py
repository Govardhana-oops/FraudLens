"""Security & Latency Benchmark Tests for Module 6."""

import time
import pytest

def test_watchlist_submillisecond_latency_benchmark(test_sync_service):
    # Seed 100 records
    records = []
    for i in range(100):
        records.append({
            "doc_number": f"PASS{i:05d}",
            "country_code": "USA",
            "category": "STOLEN_PASSPORT",
            "record_id": f"SLTD-{i:05d}",
            "reported_date": "2026-01-01",
            "severity": "CRITICAL",
            "officer_instructions": "Inspect"
        })
    test_sync_service.sync_with_server(incoming_delta=records)

    # Warmup
    test_sync_service.lookup_watchlist("PASS00050")

    t0 = time.perf_counter()
    iterations = 1000
    for _ in range(iterations):
        res = test_sync_service.lookup_watchlist("PASS00050")
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    print(f"\n[MODULE 6 BENCHMARK] Average Watchlist Lookup Latency: {avg_ms:.4f} ms/query")
    assert avg_ms < 0.20, f"Lookup latency too high: {avg_ms:.4f} ms"
