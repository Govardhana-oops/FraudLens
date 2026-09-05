"""Performance & Benchmark Testing for Module 2 Stage 3."""

import time
import pytest
from src.interface import document_validator

def test_single_document_validation_latency():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": True
        },
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }

    # Warmup
    document_validator.validate(payload)

    # Benchmark 100 iterations
    t0 = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        res = document_validator.validate(payload)
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    throughput = iterations / (t1 - t0)

    print(f"\n[BENCHMARK] Average latency: {avg_ms:.3f} ms/doc | Throughput: {throughput:.1f} docs/sec")
    assert avg_ms < 20.0, f"Average latency too high: {avg_ms:.3f} ms"
    assert res["overall_status"] == "VALID"
