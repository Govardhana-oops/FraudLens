"""Font & Character Texture Inconsistency Forensic Detector."""

from typing import Dict, Any, Optional, List
import numpy as np
import cv2
from .base_detector import BaseForensicDetector
from ..schemas.output_schema import ForensicIndicatorResult

class FontTextureDetector(BaseForensicDetector):
    """Detects localized character blur, stroke thickness anomalies, and font texture inconsistencies."""

    def detect(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> ForensicIndicatorResult:
        if image is None or image.size == 0:
            return ForensicIndicatorResult(
                name="font_texture_inconsistency",
                anomaly_score=0.0,
                confidence=0.0,
                details={"error": "Empty image buffer"}
            )

        try:
            # 1. Convert to grayscale & standard scale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY if image.shape[2] == 3 else cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()

            h, w = gray.shape
            if max(h, w) > 640:
                scale_f = 640.0 / max(h, w)
                gray_proc = cv2.resize(gray, (int(w * scale_f), int(h * scale_f)), interpolation=cv2.INTER_AREA)
            else:
                gray_proc = gray

            # 2. Extract dark text connected components using adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray_proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
            )

            # Find connected components (characters/letters)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)

            char_sharpness_list = []
            char_heights = []
            hotspots: List[List[int]] = []

            # 3. Analyze components with character-like dimensions
            for i in range(1, num_labels):
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                area = stats[i, cv2.CC_STAT_AREA]
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]

                if 8 <= h <= 60 and 4 <= w <= 50 and 20 <= area <= 1500:
                    # Crop character patch from original grayscale
                    char_crop = gray[max(0, y-2):min(gray.shape[0], y+h+2), max(0, x-2):min(gray.shape[1], x+w+2)]
                    if char_crop.size > 0:
                        # Compute local Laplacian variance (sharpness) of this character
                        lap_var = float(cv2.Laplacian(char_crop, cv2.CV_64F).var())
                        char_sharpness_list.append(lap_var)
                        char_heights.append(h)

            if len(char_sharpness_list) < 10:
                return ForensicIndicatorResult(
                    name="font_texture_inconsistency",
                    anomaly_score=0.0,
                    confidence=0.75,
                    details={"analyzed_characters": len(char_sharpness_list), "note": "Insufficient isolated characters"}
                )

            median_sharpness = float(np.median(char_sharpness_list))
            std_sharpness = float(np.std(char_sharpness_list))

            # Detect characters with anomalous sharpness
            if median_sharpness < 150.0 or std_sharpness < 100.0:
                coeff_var = 0.0
                anomaly_score = 0.0
            else:
                coeff_var = std_sharpness / (median_sharpness + 1e-4)
                anomaly_score = float(np.clip((coeff_var - 0.85) / 1.5, 0.0, 1.0))

            return ForensicIndicatorResult(
                name="font_texture_inconsistency",
                anomaly_score=round(anomaly_score, 4),
                confidence=0.86,
                details={
                    "analyzed_characters": len(char_sharpness_list),
                    "median_sharpness": round(median_sharpness, 2),
                    "std_sharpness": round(std_sharpness, 2),
                    "coefficient_of_variation": round(coeff_var, 3)
                },
                localized_hotspots=hotspots[:10]
            )
        except Exception as e:
            return ForensicIndicatorResult(
                name="font_texture_inconsistency",
                anomaly_score=0.0,
                confidence=0.5,
                details={"exception": str(e)}
            )
