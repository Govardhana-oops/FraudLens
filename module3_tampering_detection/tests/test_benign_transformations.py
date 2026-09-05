"""Benign Environmental Transformations Test Suite for Module 3."""

import pytest
import numpy as np
import cv2
from src.interface import tampering_detector
from tests.test_tampering_scenarios import _create_synthetic_id_card

def test_benign_slight_rotation():
    card = _create_synthetic_id_card()
    h, w = card.shape[:2]
    # Rotate by 2 degrees
    matrix = cv2.getRotationMatrix2D((w/2, h/2), 2.0, 1.0)
    rotated = cv2.warpAffine(card, matrix, (w, h), borderValue=(255, 255, 255))

    res = tampering_detector.analyze(rotated)
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert res["status"] != "POTENTIAL_TAMPERING"

def test_benign_lighting_gradient():
    card = _create_synthetic_id_card()
    h, w, _ = card.shape
    # Add gentle horizontal illumination gradient (room lighting)
    gradient = np.linspace(0.85, 1.15, w, dtype=np.float32)
    lit_card = np.clip(card.astype(np.float32) * gradient[None, :, None], 0, 255).astype(np.uint8)

    res = tampering_detector.analyze(lit_card)
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert res["status"] != "POTENTIAL_TAMPERING"

def test_benign_gentle_gaussian_blur():
    card = _create_synthetic_id_card()
    blurred = cv2.GaussianBlur(card, (3, 3), 0.8)

    res = tampering_detector.analyze(blurred)
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert res["status"] != "POTENTIAL_TAMPERING"

def test_benign_resolution_downscaling():
    card = _create_synthetic_id_card()
    downscaled = cv2.resize(card, (450, 300), interpolation=cv2.INTER_AREA)

    res = tampering_detector.analyze(downscaled)
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert res["status"] != "POTENTIAL_TAMPERING"
