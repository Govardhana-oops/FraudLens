"""Unit & Integration Tests for Module 1 API and Public Interface (Stage 8).

Tests:
1. GET /health endpoint
2. POST /ocr/analyze (Multipart file upload)
3. POST /ocr/analyze_json (JSON body path)
4. Invalid & Corrupted Input Handling (Empty bytes, low-res, non-existent path)
5. Structured Output Schema Adherence
"""

import io
import os
import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from src.api import app
from src.interface import document_ocr, DocumentOCR

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_image_bytes():
    # Create a 400x300 valid test image in-memory
    img = Image.new("RGB", (400, 300), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --------------------------------------------------------------------------
# 1. API HEALTH & ENDPOINT TESTS
# --------------------------------------------------------------------------

def test_api_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["module"] == "module1_ocr"
    assert data["model_version"] == "LayoutAware-MultiScale-OCR-v2.0"

def test_api_analyze_multipart_upload(client, sample_image_bytes):
    response = client.post(
        "/ocr/analyze",
        files={"file": ("test_doc.png", sample_image_bytes, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "document_type" in data
    assert "fields" in data
    assert "consistency" in data
    assert "review_required" in data

def test_api_analyze_empty_file(client):
    response = client.post(
        "/ocr/analyze",
        files={"file": ("empty.png", b"", "image/png")}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "INVALID_INPUT"

def test_api_analyze_json_path(client):
    valid_path = "data/cleaned/DOC_PASSPORT_0001_v1.png"
    if os.path.exists(valid_path):
        response = client.post("/ocr/analyze_json", json={"image_path": valid_path})
        assert response.status_code == 200
        data = response.json()
        assert data["processing_metadata"]["model_version"] == "LayoutAware-MultiScale-OCR-v2.0"

def test_api_analyze_json_missing_path(client):
    response = client.post("/ocr/analyze_json", json={"image_path": "non_existent_image.png"})
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "INVALID_INPUT"

# --------------------------------------------------------------------------
# 2. INTERFACE ROBUSTNESS & ERROR RECOVERY
# --------------------------------------------------------------------------

def test_interface_corrupted_bytes():
    res = document_ocr.process(b"CORRUPTED_RAW_IMAGE_BYTE_DATA")
    assert res["status"] == "INVALID_INPUT"
    assert res["review_required"] is True
    assert "error_details" in res

def test_interface_low_resolution():
    # 50x50 image below minimal threshold 100x100
    low_res = np.zeros((50, 50, 3), dtype=np.uint8)
    res = document_ocr.process(low_res)
    assert res["status"] == "INVALID_INPUT"
    assert res["error_details"]["type"] == "LOW_RESOLUTION"

def test_interface_numpy_array(sample_image_bytes):
    img_array = np.full((300, 400, 3), 255, dtype=np.uint8)
    res = document_ocr.process(img_array)
    assert "status" in res
    assert "document_type" in res
    assert res["processing_metadata"]["model_version"] == "LayoutAware-MultiScale-OCR-v2.0"
