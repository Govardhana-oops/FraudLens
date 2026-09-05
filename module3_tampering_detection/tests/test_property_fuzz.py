"""Property & Fuzz Testing for Module 3 Document Tampering Detection."""

import random
import pytest
import numpy as np
from src.interface import tampering_detector

@pytest.mark.parametrize("seed", range(10))
def test_fuzz_random_image_buffers_bounded_scores(seed):
    np.random.seed(seed)
    h = random.randint(200, 600)
    w = random.randint(200, 800)
    c = random.choice([1, 3])
    
    if c == 1:
        arr = np.random.randint(0, 256, (h, w), dtype=np.uint8)
    else:
        arr = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
        
    res = tampering_detector.analyze(arr)
    assert 0.0 <= res["anomaly_score"] <= 1.0
    assert 0.0 <= res["confidence"] <= 1.0
    for name, ind_score in res["indicators"].items():
        assert 0.0 <= ind_score <= 1.0, f"Indicator {name} score out of bounds: {ind_score}"

def test_tampering_determinism_invariant():
    card = np.ones((500, 700, 3), dtype=np.uint8) * 220
    res1 = tampering_detector.analyze(card)
    res2 = tampering_detector.analyze(card)
    assert res1["status"] == res2["status"]
    assert res1["anomaly_score"] == res2["anomaly_score"]
    assert res1["indicators"] == res2["indicators"]
