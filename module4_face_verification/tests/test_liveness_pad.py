"""Presentation Attack Detection (PAD) Tests for Module 4."""

import pytest
import numpy as np
import cv2
from src.liveness.pad_detector import PresentationAttackDetector
from tests.test_interface import _create_synthetic_face

@pytest.fixture
def pad_detector():
    return PresentationAttackDetector({"thresholds": {"min_liveness_score": 0.65}})

def test_genuine_face_passes_liveness(pad_detector):
    face = _create_synthetic_face()
    gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
    res = pad_detector.assess_liveness(face, gray)
    assert res.is_live is True
    assert res.liveness_score >= 0.65

def test_screen_replay_attack_detected(pad_detector):
    face = _create_synthetic_face()
    h, w, _ = face.shape
    y, x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    moire = (np.sin(x * 0.6) * np.sin(y * 0.6) * 50).astype(np.int16)
    spoofed = np.clip(face.astype(np.int16) + moire[:, :, None], 0, 255).astype(np.uint8)
    gray_spoof = cv2.cvtColor(spoofed, cv2.COLOR_RGB2GRAY)

    res = pad_detector.assess_liveness(spoofed, gray_spoof)
    assert res.is_live is False
    assert res.attack_type_detected == "screen_replay_moire_pattern"
