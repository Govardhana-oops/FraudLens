"""Image Quality Assessment for Document Screening.

Measures:
- Blur: Laplacian variance score
- Glare: Saturated pixel ratio (overexposure)
- Resolution: Dimension checks against minimum requirements
- Overall quality index [0.0 - 1.0]
"""

import cv2
import numpy as np

class ImageQualityChecker:
    def __init__(self, blur_threshold: float = 100.0, glare_threshold_ratio: float = 0.05, min_width: int = 400, min_height: int = 300):
        self.blur_threshold = blur_threshold
        self.glare_threshold_ratio = glare_threshold_ratio
        self.min_width = min_width
        self.min_height = min_height

    def assess(self, image_np: np.ndarray) -> dict:
        """Evaluates optical quality metrics on a BGR or Grayscale image."""
        if image_np is None or image_np.size == 0:
            return {
                "is_valid": False,
                "blur_score": 0.0,
                "is_blurry": True,
                "glare_ratio": 0.0,
                "has_glare": False,
                "resolution": [0, 0],
                "quality_score": 0.0,
                "status": "INVALID_IMAGE"
            }

        h, w = image_np.shape[:2]
        
        # Convert to grayscale if needed
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        # 1. Blur detection (Laplacian Variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())
        is_blurry = blur_score < self.blur_threshold

        # 2. Glare detection (Saturated pixels > 250 in 8-bit)
        saturated_pixels = np.count_nonzero(gray >= 250)
        total_pixels = gray.size
        glare_ratio = float(saturated_pixels / total_pixels) if total_pixels > 0 else 0.0
        has_glare = glare_ratio > self.glare_threshold_ratio

        # 3. Resolution adequacy
        resolution_ok = (w >= self.min_width) and (h >= self.min_height)

        # 4. Composite Quality Score [0.0, 1.0]
        # Normalize blur score (capped at 500)
        norm_blur = min(1.0, blur_score / 300.0)
        norm_glare = max(0.0, 1.0 - (glare_ratio / 0.15))
        norm_res = 1.0 if resolution_ok else 0.5

        quality_score = round(float(0.5 * norm_blur + 0.3 * norm_glare + 0.2 * norm_res), 3)

        status = "ACCEPTABLE"
        if is_blurry and has_glare:
            status = "SEVERELY_DEGRADED"
        elif is_blurry:
            status = "BLURRY"
        elif has_glare:
            status = "GLARE_DETECTED"
        elif not resolution_ok:
            status = "LOW_RESOLUTION"

        return {
            "is_valid": True,
            "width": w,
            "height": h,
            "blur_score": round(blur_score, 2),
            "is_blurry": is_blurry,
            "glare_ratio": round(glare_ratio, 4),
            "has_glare": has_glare,
            "resolution_ok": resolution_ok,
            "quality_score": quality_score,
            "status": status
        }
