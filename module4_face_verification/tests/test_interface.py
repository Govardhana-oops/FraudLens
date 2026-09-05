"""Interface & Input Decoding Tests for Module 4."""

import pytest
import numpy as np
from PIL import Image
from src.interface import face_verifier

def _create_synthetic_face(skin_val: int = 180, seed: int = 42) -> np.ndarray:
    """Generates a synthetic portrait image with eyes, nose, and mouth."""
    img = np.ones((200, 200, 3), dtype=np.uint8) * 235
    # Head contour
    cv2_img = img.copy()
    import cv2
    cv2.ellipse(cv2_img, (100, 100), (60, 80), 0, 0, 360, (skin_val, skin_val-20, skin_val-30), -1)
    # Eyes
    cv2.circle(cv2_img, (75, 80), 8, (40, 30, 20), -1)
    cv2.circle(cv2_img, (125, 80), 8, (40, 30, 20), -1)
    # Nose
    cv2.line(cv2_img, (100, 85), (100, 115), (skin_val-40, skin_val-50, skin_val-60), 3)
    # Mouth
    cv2.ellipse(cv2_img, (100, 140), (25, 10), 0, 0, 180, (140, 60, 60), 3)
    return cv2_img

def test_interface_numpy_input():
    face = _create_synthetic_face()
    res = face_verifier.verify(face, face)
    assert res["module"] == "module4_face_verification"
    assert res["status"] in ["MATCH", "REVIEW_REQUIRED"]
    assert 0.0 <= res["similarity_score"] <= 1.0

def test_interface_pil_input():
    face = _create_synthetic_face()
    pil_doc = Image.fromarray(face)
    pil_live = Image.fromarray(face)
    res = face_verifier.verify(pil_doc, pil_live)
    assert res["status"] in ["MATCH", "REVIEW_REQUIRED"]

def test_interface_empty_bytes_input():
    res = face_verifier.verify(b"", b"")
    assert res["status"] == "INVALID_INPUT"
    assert res["review_required"] is True

def test_interface_nonexistent_files():
    res = face_verifier.verify("nonexistent_doc.jpg", "nonexistent_live.jpg")
    assert res["status"] == "INVALID_INPUT"
