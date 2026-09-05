"""Universal Deep-Learning Neural OCR Engine for Identity Documents.

Provides:
1. Deep-Learning Neural OCR Engine: EasyOCR (CRAFT Text Detection + ResNet/LSTM Sequence Recognizer)
2. Spatial Bounding Box & Token Confidence Tracking
3. Multi-scale region processing (Full Document, VIZ Text Zones, High-DPI MRZ Crops)
4. Fast-path blank / unreadable image detection for zero-latency, zero-hallucination uncertainty handling
5. Fallback-safe OCR engine interface
"""

import os
import sys
import ssl
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

# Ensure SSL and UTF-8 encoding support
os.environ['PYTHONIOENCODING'] = 'utf-8'
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

_EASYOCR_READER = None

def get_easyocr_reader():
    """Lazy-load and cache the EasyOCR Reader instance (singleton)."""
    global _EASYOCR_READER
    if _EASYOCR_READER is None:
        try:
            import easyocr
            import torch
            # Optimize CPU threads for fast inference
            if hasattr(torch, 'set_num_threads'):
                torch.set_num_threads(max(1, min(4, os.cpu_count() or 2)))
            _EASYOCR_READER = easyocr.Reader(['en'], gpu=False, verbose=False)
        except Exception as e:
            print(f"[OCR Engine] EasyOCR initialization warning: {e}", file=sys.stderr)
            _EASYOCR_READER = False
    return _EASYOCR_READER if _EASYOCR_READER is not False else None


class BaseOCREngine:
    def recognize(self, image_np: np.ndarray) -> dict:
        raise NotImplementedError


class DocumentOCRBackend(BaseOCREngine):
    """Production Neural OCR Engine for Identity Documents with Spatial Layout Tracking."""

    def __init__(self, confidence_threshold: float = 0.40):
        self.confidence_threshold = confidence_threshold

    def is_blank_or_uniform(self, gray: np.ndarray) -> bool:
        """Checks if image is blank, uniform, or corrupted without wasting neural compute."""
        if gray is None or gray.size == 0:
            return True
        std = float(np.std(gray))
        mean = float(np.mean(gray))
        if std < 5.0 or mean >= 248.0 or mean <= 8.0:
            return True
        return False

    def _prepare_rgb(self, image_np: np.ndarray) -> np.ndarray:
        """Ensures image is 3-channel RGB for neural detector."""
        if len(image_np.shape) == 2:
            return cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        elif image_np.shape[2] == 4:
            return cv2.cvtColor(image_np, cv2.COLOR_BGRA2RGB)
        elif image_np.shape[2] == 3:
            # OpenCV BGR -> RGB
            return cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        return image_np

    def recognize_mrz_zone(self, mrz_crop: np.ndarray) -> List[str]:
        """Dedicated high-precision OCR on cropped MRZ zone using ICAO Doc 9303 character set."""
        reader = get_easyocr_reader()
        if reader is None or mrz_crop is None or mrz_crop.size == 0:
            return []

        rgb_mrz = self._prepare_rgb(mrz_crop)
        # Resize if small to ensure characters have >= 28px height
        h, w = rgb_mrz.shape[:2]
        if h < 120:
            scale = 140.0 / float(max(1, h))
            rgb_mrz = cv2.resize(rgb_mrz, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        try:
            detections = reader.readtext(
                rgb_mrz,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<",
                detail=1,
                paragraph=False,
                contrast_ths=0.1,
                adjust_contrast=0.5
            )
            # Sort vertically by Y coordinate, then X
            detections.sort(key=lambda d: (d[0][0][1], d[0][0][0]))
            
            lines = []
            for bbox, text, conf in detections:
                t = text.strip().upper().replace(" ", "<")
                if t and len(t) >= 10:
                    lines.append(t)
            return lines
        except Exception:
            return []

    def recognize(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> dict:
        """Executes full document neural OCR, extracts bounding boxes, and fuses MRZ crop."""
        if image_np is None or image_np.size == 0:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "easyocr_neural_reader"
            }

        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        # Blank canvas fast-path
        if self.is_blank_or_uniform(gray):
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "easyocr_neural_reader"
            }

        reader = get_easyocr_reader()
        if reader is None:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "offline_uninitialized"
            }

        rgb_img = self._prepare_rgb(image_np)
        h, w = rgb_img.shape[:2]

        try:
            # 1. Full Image Detection
            detections = reader.readtext(
                rgb_img,
                detail=1,
                paragraph=False,
                contrast_ths=0.1,
                adjust_contrast=0.5
            )
        except Exception as e:
            detections = []

        # Sort detections by Y then X
        detections.sort(key=lambda item: (item[0][0][1], item[0][0][0]))

        lines = []
        words_metadata = []
        confidences = []

        for bbox, text, conf in detections:
            t = text.strip()
            if t:
                lines.append(t)
                conf_val = float(conf)
                confidences.append(conf_val)
                xs = [pt[0] for pt in bbox]
                ys = [pt[1] for pt in bbox]
                words_metadata.append({
                    "text": t,
                    "confidence": round(conf_val, 2),
                    "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
                })

        # 2. Dedicated MRZ Stream Recognition if bottom region has dense text or crop provided
        mrz_detected_lines = []
        if mrz_crop is not None and mrz_crop.size > 0:
            mrz_detected_lines = self.recognize_mrz_zone(mrz_crop)
        else:
            # Automatic MRZ band crop (bottom 28%)
            mrz_band_y = int(h * 0.72)
            auto_mrz_crop = image_np[mrz_band_y:, :]
            mrz_detected_lines = self.recognize_mrz_zone(auto_mrz_crop)

        # Merge MRZ lines if not already accurately captured in full OCR
        for ml in mrz_detected_lines:
            # Check if this MRZ line is already present
            ml_clean = ml.replace("<", "")[:12]
            if ml_clean and not any(ml_clean in line.replace("<", "") for line in lines):
                lines.append(ml)

        raw_text = "\n".join(lines).strip()
        avg_conf = float(np.mean(confidences)) if confidences else 0.0

        return {
            "raw_text": raw_text,
            "lines": lines,
            "words": words_metadata,
            "average_confidence": round(avg_conf, 3),
            "engine": "easyocr_neural_reader"
        }


class OCREngine:
    def __init__(self, confidence_threshold: float = 0.40):
        self.backend = DocumentOCRBackend(confidence_threshold=confidence_threshold)

    def extract_text(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> dict:
        return self.backend.recognize(image_np, mrz_crop=mrz_crop)

