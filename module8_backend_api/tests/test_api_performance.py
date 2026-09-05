"""API Performance & Throughput Benchmark Tests for Module 8."""

import io
import time
import pytest
from PIL import Image

def _create_dummy_image_bytes():
    img = Image.new("RGB", (100, 100), color=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_api_screening_latency_benchmark(client):
    doc_bytes = _create_dummy_image_bytes()
    files = {"document_file": ("test_doc.jpg", doc_bytes, "image/jpeg")}

    # Warmup
    client.post("/api/v1/screening/inspect", files=files)

    t0 = time.perf_counter()
    iterations = 15
    for _ in range(iterations):
        res = client.post("/api/v1/screening/inspect", files=files)
        assert res.status_code == 200
    t1 = time.perf_counter()

    avg_ms = ((t1 - t0) / iterations) * 1000.0
    print(f"\n[MODULE 8 BENCHMARK] Average REST Screening Endpoint Latency: {avg_ms:.2f} ms/req")
    assert avg_ms < 200.0, f"HTTP Screening latency too high: {avg_ms:.2f} ms"
