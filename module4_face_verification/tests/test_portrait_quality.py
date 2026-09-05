"""ICAO Doc 9303 Face Quality Tests for Module 4."""

import pytest
import numpy as np
import cv2
from src.quality.portrait_quality_evaluator import PortraitQualityEvaluator
from tests.test_interface import _create_synthetic_face

@pytest.fixture
def quality_evaluator():
    return PortraitQualityEvaluator({
        "thresholds": {
            "min_sharpness_score": 20.0,
            "min_illumination_uniformity": 0.60,
            "max_glare_percentage": 5.0
        }
    })

def test_sharp_face_passes_quality(quality_evaluator):
    face = _create_synthetic_face()
    qa, crop = quality_evaluator.evaluate(face)
    assert crop is not None
    assert qa.sharpness >= 15.0
    assert 0.0 <= qa.overall_quality_score <= 1.0

def test_blurry_face_triggers_warning(quality_evaluator):
    face = _create_synthetic_face()
    blurry = cv2.GaussianBlur(face, (15, 15), 5.0)
    qa, crop = quality_evaluator.evaluate(blurry)
    assert qa.sharpness < 20.0
    assert not qa.is_compliant

def test_no_face_detected_empty_image(quality_evaluator):
    empty = np.ones((100, 100, 3), dtype=np.uint8) * 255
    qa, crop = quality_evaluator.evaluate(empty)
    assert qa.overall_quality_score == 0.0
    assert "No frontal face detected" in qa.warnings[0] or not qa.is_compliant
