"""Optimized & Vectorized Noise Inconsistency Forensic Detector."""

from typing import Dict, Any, Optional, List
import numpy as np
import cv2
from .base_detector import BaseForensicDetector
from ..schemas.output_schema import ForensicIndicatorResult

class NoiseInconsistencyDetector(BaseForensicDetector):
    """Detects localized sensor noise variance discrepancies indicating spliced image patches."""

    def detect(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> ForensicIndicatorResult:
        if image is None or image.size == 0:
            return ForensicIndicatorResult(
                name="noise_inconsistency",
                anomaly_score=0.0,
                confidence=0.0,
                details={"error": "Empty image buffer"}
            )

        try:
            # 1. Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY if image.shape[2] == 3 else cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()

            # 2. Extract high-frequency noise residual using median filtering subtraction
            blurred = cv2.medianBlur(gray, 3)
            noise_residual = cv2.absdiff(gray, blurred).astype(np.float32)

            # 3. Fast Vectorized local variance mapping using boxFilter
            patch_size = self.config.get("noise_params", {}).get("patch_size", 32)
            mean_noise = cv2.boxFilter(noise_residual, -1, (patch_size, patch_size), normalize=True)
            sq_mean_noise = cv2.boxFilter(noise_residual**2, -1, (patch_size, patch_size), normalize=True)
            local_var = np.maximum(0.0, sq_mean_noise - (mean_noise**2))

            # Downsample local variance map to patch grid
            h, w = local_var.shape
            grid_h, grid_w = h // patch_size, w // patch_size
            if grid_h == 0 or grid_w == 0:
                return ForensicIndicatorResult(
                    name="noise_inconsistency",
                    anomaly_score=0.0,
                    confidence=0.7,
                    details={"note": "Image too small for patch variance"}
                )

            # Subsample grid values
            sampled_vars = local_var[::patch_size, ::patch_size].flatten()

            median_var = float(np.median(sampled_vars))
            p75 = float(np.percentile(sampled_vars, 75))
            p25 = float(np.percentile(sampled_vars, 25))
            iqr = max(p75 - p25, 1e-4)

            # Hotspots: regions where noise variance deviates by > 3.5 IQR
            hotspots: List[List[int]] = []
            outlier_mask = (local_var > (p75 + (3.5 * iqr))).astype(np.uint8)
            contours, _ = cv2.findContours(outlier_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w_b, h_b = cv2.boundingRect(cnt)
                if w_b >= 16 and h_b >= 16:
                    hotspots.append([int(y), int(x), int(y + h_b), int(x + w_b)])

            if median_var < 1.0 or iqr < 0.5:
                dispersion_ratio = 0.0
                anomaly_score = 0.0
            else:
                dispersion_ratio = iqr / (median_var + 1e-4)
                # Uniform recompression increases median_var evenly without blowing up dispersion_ratio
                anomaly_score = float(np.clip((dispersion_ratio - 0.75) / 2.2, 0.0, 1.0))

            return ForensicIndicatorResult(
                name="noise_inconsistency",
                anomaly_score=round(anomaly_score, 4),
                confidence=0.90,
                details={
                    "median_noise_variance": round(median_var, 3),
                    "iqr": round(iqr, 3),
                    "dispersion_ratio": round(dispersion_ratio, 3),
                    "hotspot_count": len(hotspots)
                },
                localized_hotspots=hotspots[:10]
            )
        except Exception as e:
            return ForensicIndicatorResult(
                name="noise_inconsistency",
                anomaly_score=0.0,
                confidence=0.5,
                details={"exception": str(e)}
            )
