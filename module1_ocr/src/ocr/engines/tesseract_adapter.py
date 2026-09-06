"""PyTesseract Engine Adapter for Module 1 (Imported from Phone OCR)."""

import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from .base_engine import BaseOCREngine

class PyTesseractAdapter(BaseOCREngine):
    """PyTesseract Engine Adapter conforming to Module 1 standard interface."""

    def __init__(self):
        self._pytesseract = None
        self._available = False
        self._init_engine()

    def _init_engine(self):
        try:
            import pytesseract
            self._pytesseract = pytesseract
            self._pytesseract.get_tesseract_version()
            self._available = True
        except Exception:
            self._available = False

    @property
    def name(self) -> str:
        return "tesseract_adapter"

    def is_available(self) -> bool:
        return self._available

    def recognize(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Executes text recognition using PyTesseract."""
        if image_np is None or image_np.size == 0:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": self.name
            }

        if not self._available or self._pytesseract is None:
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "tesseract_unavailable"
            }

        # Convert to RGB for Tesseract
        if len(image_np.shape) == 2:
            rgb_img = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
        elif image_np.shape[2] == 4:
            rgb_img = cv2.cvtColor(image_np, cv2.COLOR_BGRA2RGB)
        elif image_np.shape[2] == 3:
            rgb_img = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        else:
            rgb_img = image_np

        lines = []
        words_metadata = []
        confidences = []

        try:
            data = self._pytesseract.image_to_data(rgb_img, output_type=self._pytesseract.Output.DICT)
            n_boxes = len(data.get('text', []))
            current_line = []

            for i in range(n_boxes):
                text = str(data['text'][i]).strip()
                conf_raw = float(data['conf'][i])
                if text and conf_raw > 0:
                    conf_val = round(conf_raw / 100.0, 3)
                    confidences.append(conf_val)
                    x, y, w, h = int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])
                    words_metadata.append({
                        "text": text,
                        "confidence": conf_val,
                        "bbox": [x, y, x + w, y + h]
                    })
                    current_line.append(text)

            # Get full text line breaks
            full_text = self._pytesseract.image_to_string(rgb_img).strip()
            lines = [l.strip() for l in full_text.splitlines() if l.strip()]
        except Exception as e:
            print(f"[PyTesseract Adapter Warning] Text extraction error: {e}")

        # Supplementary MRZ pass if provided
        if mrz_crop is not None and mrz_crop.size > 0:
            try:
                mrz_rgb = cv2.cvtColor(mrz_crop, cv2.COLOR_BGR2RGB) if len(mrz_crop.shape) == 3 else mrz_crop
                mrz_text = self._pytesseract.image_to_string(
                    mrz_rgb,
                    config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
                ).strip()
                for l in mrz_text.splitlines():
                    clean_l = l.strip().upper().replace(" ", "<")
                    if len(clean_l) >= 10:
                        lines.append(clean_l)
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
