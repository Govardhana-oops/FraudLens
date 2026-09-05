"""Unit Tests for Module 3 Public Interface."""

import pytest
import numpy as np
from PIL import Image
from src.interface import tampering_detector

def test_interface_numpy_input():
    # 512x512 RGB uniform card background
    arr = np.ones((512, 512, 3), dtype=np.uint8) * 230
    res = tampering_detector.analyze(arr)
    assert res["module"] == "module3_tampering_detection"
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert 0.0 <= res["anomaly_score"] <= 1.0

def test_interface_pil_input():
    pil_img = Image.new("RGB", (400, 300), color=(240, 240, 240))
    res = tampering_detector.analyze(pil_img)
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]

def test_interface_empty_bytes():
    res = tampering_detector.analyze(b"")
    assert res["status"] == "INVALID_INPUT"
    assert res["review_required"] is True

def test_interface_nonexistent_file():
    res = tampering_detector.analyze("nonexistent_image_path_123.jpg")
    assert res["status"] == "INVALID_INPUT"
    assert len(res["errors"]) > 0

def test_interface_low_resolution_safety():
    tiny_arr = np.ones((50, 50, 3), dtype=np.uint8) * 200
    res = tampering_detector.analyze(tiny_arr)
    assert res["status"] == "UNKNOWN"
    assert res["review_required"] is True
