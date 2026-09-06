"""EasyOCR Engine Adapter for Module 1 (Imported from Phone OCR)."""

import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from .base_engine import BaseOCREngine

class EasyOCRAdapter(BaseOCREngine):
    """EasyOCR Engine Adapter conforming to Module 1 standard interface."""

    def __init__(self):
        self._reader = None
        self._available = False
        self._init_engine()

    def _init_engine(self):
        try:
            import easyocr
            self._easyocr_module = easyocr
            self._available = True
        except Exception:
            self._available = False

    def _get_reader(self):
        if self._reader is None and self._available:
            self._reader = self._easyocr_module.Reader(['en'], gpu=False, verbose=False)
        return self._reader

    @property
    def name(self) -> str:
        return "easyocr_adapter"

    def is_available(self) -> bool:
        return self._available

    def recognize(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Executes text recognition using EasyOCR."""
        if image_np is None or image_np.size == 0:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": self.name
            }

        reader = self._get_reader()
        if not self._available or reader is None:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "easyocr_unavailable"
            }

        # Convert to BGR if grayscale
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
            results = reader.readtext(bgr_img)
            # Sort by Y then X
            results.sort(key=lambda item: (item[0][0][1], item[0][0][0]))

            for bbox_raw, text, conf in results:
                t = text.strip()
                if t:
                    lines.append(t)
                    conf_val = float(conf)
                    confidences.append(conf_val)
                    xs = [int(pt[0]) for pt in bbox_raw]
                    ys = [int(pt[1]) for pt in bbox_raw]
                    words_metadata.append({
                        "text": t,
                        "confidence": round(conf_val, 2),
                        "bbox": [min(xs), min(ys), max(xs), max(ys)]
                    })
        except Exception as e:
            print(f"[EasyOCR Adapter Warning] Text extraction error: {e}")

        # If MRZ crop is supplied, perform supplementary MRZ extraction
        if mrz_crop is not None and mrz_crop.size > 0:
            try:
                mrz_results = reader.readtext(
                    mrz_crop,
                    allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
                )
                for bbox_raw, text, conf in mrz_results:
                    t = text.strip().upper().replace(" ", "<")
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
