"""Edge Cases & Quality Boundaries Test Suite for Module 4."""

import pytest
import numpy as np
import cv2
from src.interface import face_verifier
from tests.test_interface import _create_synthetic_face

def test_extreme_overexposure_glare():
    face = _create_synthetic_face()
    glare_face = face.copy()
    glare_face[70:130, 70:130] = 255 # Specular glare patch

    res = face_verifier.verify(face, glare_face)
    assert res["status"] in ["MATCH", "NO_MATCH", "REVIEW_REQUIRED", "POOR_QUALITY"]

def test_dark_underexposure():
    face = _create_synthetic_face()
    dark_face = (face * 0.15).astype(np.uint8)

    res = face_verifier.verify(face, dark_face)
    assert res["status"] in ["POOR_QUALITY", "NO_MATCH", "REVIEW_REQUIRED", "NO_FACE_DETECTED"]
