"""End-to-End Synthetic Tampering Scenarios Test Suite."""

import io
import pytest
import numpy as np
import cv2
from PIL import Image
from src.interface import tampering_detector

def _create_synthetic_id_card() -> np.ndarray:
    """Generates a clean synthetic identity document card."""
    card = np.ones((600, 900, 3), dtype=np.uint8) * 240
    # Add subtle guilloche/security pattern
    for y in range(0, 600, 20):
        cv2.line(card, (0, y), (900, y), (230, 235, 245), 1)
    # Add portrait box
    cv2.rectangle(card, (50, 100), (280, 420), (180, 180, 180), 2)
    # Add synthetic portrait
    card[102:418, 52:278] = 200
    # Add text lines
    cv2.putText(card, "PASSPORT / PASSEPORT", (320, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
    cv2.putText(card, "DOE, JOHN", (320, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.putText(card, "P12345678", (320, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    cv2.putText(card, "DOB: 12 AUG 1985", (320, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 2)
    # Add MRZ
    cv2.putText(card, "P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", (50, 520), cv2.FONT_HERSHEY_PLAIN, 1.2, (20, 20, 20), 2)
    cv2.putText(card, "P123456789USA8508124M3008258<<<<<<<<<<<<<<<8", (50, 560), cv2.FONT_HERSHEY_PLAIN, 1.2, (20, 20, 20), 2)
    return card

def test_pristine_document_no_tampering():
    card = _create_synthetic_id_card()
    res = tampering_detector.analyze(card)
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert res["anomaly_score"] < 0.50

def test_spliced_photo_replacement_tampering():
    card = _create_synthetic_id_card()
    # Paste an external photo with distinct noise and sharp rectangular clipping
    np.random.seed(99)
    imposter_photo = np.random.normal(120, 35, (316, 226, 3)).astype(np.uint8)
    card[102:418, 52:278] = imposter_photo

    res = tampering_detector.analyze(card)
    # Anomaly score should be elevated due to noise variance and edge discontinuities
    assert res["anomaly_score"] > 0.30
    assert res["status"] in ["POTENTIAL_TAMPERING", "REVIEW_REQUIRED"]

def test_screen_replay_moire_tampering():
    card = _create_synthetic_id_card()
    # Add periodic sinusoidal 2D moiré pattern
    h, w, _ = card.shape
    y, x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    moire = (np.sin(x * 0.4) * np.sin(y * 0.4) * 40).astype(np.int16)
    card_moire = np.clip(card.astype(np.int16) + moire[:, :, None], 0, 255).astype(np.uint8)

    res = tampering_detector.analyze(card_moire)
    assert res["indicators"]["frequency_fft_spectral"] > 0.35
    assert res["status"] in ["POTENTIAL_TAMPERING", "REVIEW_REQUIRED"]

def test_benign_jpeg_recompression():
    card = _create_synthetic_id_card()
    # Save as standard JPEG at Q=80 and reload
    pil_card = Image.fromarray(card)
    buf = io.BytesIO()
    pil_card.save(buf, format="JPEG", quality=80)
    buf.seek(0)
    recompressed = np.array(Image.open(buf))

    res = tampering_detector.analyze(recompressed)
    # Benign recompression without localized edits should NOT produce POTENTIAL_TAMPERING
    assert res["status"] in ["NO_TAMPERING_EVIDENCE", "REVIEW_REQUIRED"]
    assert res["anomaly_score"] < 0.60
