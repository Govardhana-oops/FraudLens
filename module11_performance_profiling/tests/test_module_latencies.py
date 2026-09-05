"""Per-Module Microsecond Latency Profiling for Module 11."""

import pytest
import numpy as np
from PIL import Image

from module2_document_validation.src.interface import document_validator
from module3_tampering_detection.src.interface import tampering_detector
from module4_face_verification.src.interface import face_verifier
from module5_explainable_evidence.src.interface import evidence_fusion_engine
from module6_database_sync.src.interface import database_sync_service
from module11_performance_profiling.src.profiler import PerformanceProfiler

def test_module2_rule_validation_latency():
    sample_m1 = {
        "module": "module1_ocr",
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.98},
        "fields": {
            "passport_number": {"value": "P12345678", "confidence": 0.95},
            "full_name": {"value": "JOHN DOE", "confidence": 0.99},
            "nationality": {"value": "USA", "confidence": 0.99},
            "date_of_birth": {"value": "1990-05-15", "confidence": 0.98},
            "date_of_expiry": {"value": "2030-05-14", "confidence": 0.98},
            "issuing_country": {"value": "USA", "confidence": 0.99}
        },
        "mrz": {
            "status": "VALID",
            "mrz_format": "TD3",
            "lines": [
                "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
                "P123456789USA9005156M3005143<<<<<<<<<<<<<<<8"
            ],
            "checksum_valid": True,
            "checks": {"composite": True}
        },
        "visual_mrz_conflicts": []
    }
    stats = PerformanceProfiler.measure_latency_percentiles(
        lambda: document_validator.validate(sample_m1),
        iterations=50
    )
    print(f"\n[M2 LATENCY] Mean: {stats['mean_ms']:.4f} ms | P99: {stats['p99_ms']:.4f} ms")
    assert stats["p99_ms"] < 10.0, f"Module 2 P99 too slow: {stats['p99_ms']} ms"

def test_module3_tampering_detection_latency():
    doc_img = np.ones((250, 350, 3), dtype=np.uint8) * 230
    stats = PerformanceProfiler.measure_latency_percentiles(
        lambda: tampering_detector.analyze(doc_img),
        iterations=30
    )
    print(f"\n[M3 LATENCY] Mean: {stats['mean_ms']:.4f} ms | P99: {stats['p99_ms']:.4f} ms")
    assert stats["p99_ms"] < 60.0, f"Module 3 P99 too slow: {stats['p99_ms']} ms"

def test_module4_face_verification_latency():
    doc_img = np.ones((150, 150, 3), dtype=np.uint8) * 220
    live_img = np.ones((150, 150, 3), dtype=np.uint8) * 225
    stats = PerformanceProfiler.measure_latency_percentiles(
        lambda: face_verifier.verify(doc_img, live_img),
        iterations=30
    )
    print(f"\n[M4 LATENCY] Mean: {stats['mean_ms']:.4f} ms | P99: {stats['p99_ms']:.4f} ms")
    assert stats["p99_ms"] < 50.0, f"Module 4 P99 too slow: {stats['p99_ms']} ms"

def test_module5_evidence_fusion_latency():
    stats = PerformanceProfiler.measure_latency_percentiles(
        lambda: evidence_fusion_engine.assess(
            {"document_type": {"value": "passport"}},
            {"overall_status": "VALID"},
            {"status": "CLEAN"},
            {"status": "MATCH", "similarity_score": 0.95}
        ),
        iterations=50
    )
    print(f"\n[M5 LATENCY] Mean: {stats['mean_ms']:.4f} ms | P99: {stats['p99_ms']:.4f} ms")
    assert stats["p99_ms"] < 2.0, f"Module 5 P99 too slow: {stats['p99_ms']} ms"

def test_module6_database_lookup_latency():
    stats = PerformanceProfiler.measure_latency_percentiles(
        lambda: database_sync_service.lookup_watchlist("P12345678", "USA"),
        iterations=100
    )
    print(f"\n[M6 LATENCY] Mean: {stats['mean_ms']:.4f} ms | P99: {stats['p99_ms']:.4f} ms")
    assert stats["p99_ms"] < 1.0, f"Module 6 P99 too slow: {stats['p99_ms']} ms"
