"""Illumination & Environmental Variance Tests for Module 4."""

import pytest
import numpy as np
import cv2
from src.interface import face_verifier
from tests.test_interface import _create_synthetic_face

def test_side_lighting_shadow_warning():
    face = _create_synthetic_face()
    h, w, _ = face.shape
    # Add realistic side lighting gradient
    gradient = np.linspace(0.4, 1.0, w, dtype=np.float32)
    shadowed = np.clip(face.astype(np.float32) * gradient[None, :, None], 0, 255).astype(np.uint8)

    res = face_verifier.verify(face, shadowed)
    assert res["status"] in ["MATCH", "REVIEW_REQUIRED"]

def test_slight_head_tilt_invariance():
    face = _create_synthetic_face()
    h, w = face.shape[:2]
    # Rotate by 4 degrees
    matrix = cv2.getRotationMatrix2D((w/2, h/2), 4.0, 1.0)
    tilted = cv2.warpAffine(face, matrix, (w, h), borderValue=(235, 235, 235))

    res = face_verifier.verify(face, tilted)
    assert res["status"] == "MATCH"
    assert res["similarity_score"] >= 0.70
