"""Document Type Classifier for AI-DIDSS Module 1.

Implements conservative multi-cue document classification:
- Visual Header & Body Keywords
- MRZ Geometry & Syntax (TD1, TD2, TD3, MRV-A, MRV-B)
- Safe fallback to 'unknown_document' when confidence is insufficient
"""

import re
from typing import Tuple, Optional, Any

class DocumentTypeClassifier:
    def __init__(self, min_confidence: float = 0.50):
        self.min_confidence = min_confidence

    def classify(self, raw_text: str, mrz_validation: Optional[Any] = None) -> Tuple[str, float]:
        text_upper = raw_text.upper()
        scores = {
            "passport": 0.0,
            "visa": 0.0,
            "driver_license": 0.0,
            "national_id": 0.0,
            "permit": 0.0
        }

        # 1. Visual Text Cues
        if "PASSPORT" in text_upper or "PASSEPORT" in text_upper:
            scores["passport"] += 0.60
        if "TRAVEL VISA" in text_upper or "VISA NO" in text_upper or "VISA TYPE" in text_upper:
            scores["visa"] += 0.60
        if "DRIVER LICENSE" in text_upper or "DRIVING LICENCE" in text_upper or "DL NO" in text_upper or "DRIVER'S LICENSE" in text_upper:
            scores["driver_license"] += 0.70
        if "RESIDENCE" in text_upper or "PERMIT NO" in text_upper or "WORK PERMIT" in text_upper:
            scores["permit"] += 0.70
        if "NATIONAL IDENTITY" in text_upper or "NATIONAL ID" in text_upper or "CITIZEN ID" in text_upper:
            scores["national_id"] += 0.65

        # 2. MRZ Structural Cues
        if mrz_validation and mrz_validation.mrz_format:
            fmt = mrz_validation.mrz_format
            if fmt == "TD3":
                scores["passport"] += 0.50
            elif fmt in ["MRV_A", "MRV_B"]:
                scores["visa"] += 0.50
            elif fmt == "TD1":
                scores["national_id"] += 0.45

        # 3. Field Anchor Cues
        if re.search(r"DL-[A-Z0-9]+", text_upper):
            scores["driver_license"] += 0.30
        if re.search(r"RP-[A-Z0-9]+", text_upper):
            scores["permit"] += 0.30
        if re.search(r"ID-[A-Z0-9]+", text_upper):
            scores["national_id"] += 0.30

        # Determine highest scoring candidate
        best_doc, best_score = max(scores.items(), key=lambda item: item[1])

        if best_score < self.min_confidence:
            return "unknown_document", 0.0

        confidence = min(round(best_score, 2), 0.99)
        return best_doc, confidence
