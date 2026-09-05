"""Unit Tests for Image Preprocessing Pipeline."""

import cv2
import numpy as np
import pytest
from src.preprocessing.quality_check import ImageQualityChecker
from src.preprocessing.illumination import IlluminationNormalizer
from src.preprocessing.deskew import DocumentDeskewer
from src.preprocessing.pipeline import PreprocessingPipeline

def test_quality_checker_valid():
    checker = ImageQualityChecker()
    # Create sharp, clear synthetic image
    img = np.ones((600, 800, 3), dtype=np.uint8) * 128
    cv2.putText(img, "TEST DOCUMENT OCR SHARP", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    
    report = checker.assess(img)
    assert report["is_valid"] is True
    assert report["width"] == 800
    assert report["height"] == 600
    assert report["quality_score"] > 0.50

def test_quality_checker_invalid_empty():
    checker = ImageQualityChecker()
    report = checker.assess(None)
    assert report["is_valid"] is False
    assert report["status"] == "INVALID_IMAGE"

def test_illumination_normalizer():
    norm = IlluminationNormalizer()
    img = np.zeros((400, 600, 3), dtype=np.uint8) + 50
    enhanced = norm.normalize(img, auto_gamma=True)
    assert enhanced.shape == img.shape
    assert np.mean(enhanced) >= np.mean(img)

def test_deskewer():
    deskewer = DocumentDeskewer()
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    res, angle = deskewer.deskew(img)
    assert res is not None
    assert abs(angle) < 45.0

def test_preprocessing_pipeline():
    pipeline = PreprocessingPipeline(mode="standard")
    img = np.ones((500, 700, 3), dtype=np.uint8) * 200
    cv2.putText(img, "PASSPORT TD3 TEST", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (20, 20, 20), 2)
    
    res = pipeline.process_image(img)
    assert "processed_image" in res
    assert "quality_assessment" in res
    assert "transformations_applied" in res
    assert res["quality_assessment"]["is_valid"] is True
