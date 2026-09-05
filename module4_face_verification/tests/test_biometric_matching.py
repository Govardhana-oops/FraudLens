"""Biometric 1:1 Matching Tests (Genuine Match vs Imposter Mismatch)."""

import pytest
import numpy as np
from src.interface import face_verifier
from tests.test_interface import _create_synthetic_face

def test_genuine_face_match():
    person_a = _create_synthetic_face(skin_val=190, seed=1)
    res = face_verifier.verify(person_a, person_a)
    assert res["status"] == "MATCH"
    assert res["similarity_score"] >= 0.85
    assert res["review_required"] is False

def test_imposter_face_mismatch():
    import cv2
    # Person A
    person_a = _create_synthetic_face(skin_val=200, seed=10)
    # Person B (very different morphology: small face, dark skin, inverted eyes)
    person_b = np.ones((200, 200, 3), dtype=np.uint8) * 235
    cv2.ellipse(person_b, (100, 100), (30, 40), 0, 0, 360, (70, 50, 40), -1)
    cv2.circle(person_b, (90, 85), 3, (250, 250, 250), -1)
    cv2.circle(person_b, (110, 85), 3, (250, 250, 250), -1)
    cv2.line(person_b, (100, 90), (100, 110), (30, 20, 10), 1)

    res = face_verifier.verify(person_a, person_b)
    # Should result in NO_MATCH or REVIEW_REQUIRED
    assert res["status"] in ["NO_MATCH", "REVIEW_REQUIRED"]
    assert res["similarity_score"] < 0.70
