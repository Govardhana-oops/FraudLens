"""PaddleOCR Engine Adapter for Module 1 (Imported from Phone OCR)."""

import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from .base_engine import BaseOCREngine

class PaddleOCRAdapter(BaseOCREngine):
    """PaddleOCR Engine Adapter conforming to Module 1 standard interface."""

    def __init__(self):
        self._ocr = None
        self._available = False
        self._init_engine()

    def _init_engine(self):
        try:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            self._available = True
        except Exception:
            self._available = False

    @property
    def name(self) -> str:
        return "paddleocr_adapter"

    def is_available(self) -> bool:
        return self._available

    def recognize(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Executes text recognition using PaddleOCR."""
        if image_np is None or image_np.size == 0:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": self.name
            }

        if not self._available or self._ocr is None:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "paddleocr_unavailable"
            }

        # Convert to BGR format
        if len(image_np.shape) == 2:
            bgr_img = cv2.cvtColor(image_np, cv2.COLOR_GRAY2BGR)
        elif image_np.shape[2] == 4:
            bgr_img = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)
        else:
            bgr_img = image_np

        lines = []
        words_metadata = []
        confidences = []

        try:
            results = self._ocr.ocr(bgr_img, cls=True)
            if results and results[0]:
                for line in results[0]:
                    bbox = [[int(pt[0]), int(pt[1])] for pt in line[0]]
                    text = line[1][0].strip()
                    confidence = float(line[1][1])

                    if text:
                        lines.append(text)
                        confidences.append(confidence)
                        xs = [pt[0] for pt in bbox]
                        ys = [pt[1] for pt in bbox]
                        words_metadata.append({
                            "text": text,
                            "confidence": round(confidence, 2),
                            "bbox": [min(xs), min(ys), max(xs), max(ys)]
                        })
        except Exception as e:
            print(f"[PaddleOCR Adapter Warning] Text extraction error: {e}")

        # If MRZ crop is supplied, perform supplementary MRZ extraction
        if mrz_crop is not None and mrz_crop.size > 0:
            try:
                mrz_results = self._ocr.ocr(mrz_crop, cls=False)
                if mrz_results and mrz_results[0]:
                    for line in mrz_results[0]:
                        t = line[1][0].strip().upper().replace(" ", "<")
                        if t and len(t) >= 10:
                            lines.append(t)
            except Exception:
                pass

        raw_text = "\n".join(lines).strip()
        avg_conf = float(np.mean(confidences)) if confidences else 0.0

        return {
            "raw_text": raw_text,
            "lines": lines,
            "words": words_metadata,
            "average_confidence": round(avg_conf, 3),
            "engine": self.name
        }
