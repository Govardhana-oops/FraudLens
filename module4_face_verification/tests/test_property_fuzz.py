"""Property & Fuzz Testing for Module 4 Face Verification."""

import random
import pytest
import numpy as np
from src.interface import face_verifier
from tests.test_interface import _create_synthetic_face

@pytest.mark.parametrize("seed", range(10))
def test_fuzz_random_image_pairs_bounded_scores(seed):
    np.random.seed(seed)
    h = random.randint(100, 300)
    w = random.randint(100, 300)
    arr_a = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    arr_b = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)

    res = face_verifier.verify(arr_a, arr_b)
    assert 0.0 <= res["similarity_score"] <= 1.0
    assert 0.0 <= res["confidence"] <= 1.0
    assert res["status"] in ["MATCH", "NO_MATCH", "REVIEW_REQUIRED", "POOR_QUALITY", "NO_FACE_DETECTED", "SPOOF_ATTEMPT_DETECTED"]

def test_biometric_symmetry_invariant():
    face_a = _create_synthetic_face(skin_val=180, seed=5)
    face_b = _create_synthetic_face(skin_val=150, seed=6)

    res_ab = face_verifier.verify(face_a, face_b)
    res_ba = face_verifier.verify(face_b, face_a)

    assert res_ab["status"] == res_ba["status"]
    assert abs(res_ab["similarity_score"] - res_ba["similarity_score"]) < 1e-3
