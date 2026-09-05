"""Localized Region Forensics Test Suite for Module 3."""

import pytest
import numpy as np
import cv2
from src.interface import tampering_detector
from tests.test_tampering_scenarios import _create_synthetic_id_card

def test_photo_region_splicing_localization():
    card = _create_synthetic_id_card()
    # Splice portrait area with distinct high noise
    np.random.seed(42)
    spliced_photo = np.random.normal(100, 40, (316, 226, 3)).astype(np.uint8)
    card[102:418, 52:278] = spliced_photo

    regions = {
        "photo": [100, 50, 420, 280],
        "mrz": [500, 50, 580, 850]
    }

    res = tampering_detector.analyze(card, regions=regions)
    assert res["status"] in ["POTENTIAL_TAMPERING", "REVIEW_REQUIRED"]
    assert res["anomaly_score"] > 0.35

def test_text_line_modification_detection():
    card = _create_synthetic_id_card()
    # Modify DOB by painting white rectangle and pasting mismatched digital text
    card[275:305, 380:550] = 240
    cv2.putText(card, "DOB: 01 JAN 2005", (380, 295), cv2.FONT_HERSHEY_TRIPLEX, 0.7, (0, 0, 0), 2)

    res = tampering_detector.analyze(card)
    assert res["status"] in ["POTENTIAL_TAMPERING", "REVIEW_REQUIRED"]
