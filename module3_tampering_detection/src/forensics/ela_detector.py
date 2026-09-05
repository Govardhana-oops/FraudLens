"""Optimized & Vectorized Error Level Analysis (ELA) Forensic Detector."""

import io
from typing import Dict, Any, Optional, List
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageChops
from .base_detector import BaseForensicDetector
from ..schemas.output_schema import ForensicIndicatorResult

class ELADetector(BaseForensicDetector):
    """Detects JPEG compression error discrepancies across image regions."""

    def detect(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> ForensicIndicatorResult:
        if image is None or image.size == 0:
            return ForensicIndicatorResult(
                name="error_level_analysis",
                anomaly_score=0.0,
                confidence=0.0,
                details={"error": "Empty or null image buffer"}
            )

        try:
            # 1. Convert numpy array to PIL Image
            if len(image.shape) == 2:
                pil_orig = Image.fromarray(image).convert("RGB")
            else:
                pil_orig = Image.fromarray(image[:, :, :3]).convert("RGB")

            # 2. Resave to in-memory JPEG buffer at target quality factor
            quality = self.config.get("ela_params", {}).get("quality", 90)
            scale = self.config.get("ela_params", {}).get("scale", 15)

            buf = io.BytesIO()
            pil_orig.save(buf, format="JPEG", quality=quality)
            buf.seek(0)
            pil_resaved = Image.open(buf)

            # 3. Compute absolute difference between original and recompressed
            diff = ImageChops.difference(pil_orig, pil_resaved)

            # 4. Scale difference for statistical sensitivity
            diff_arr = np.array(diff, dtype=np.float32)
            gray_diff = cv2.cvtColor(diff_arr.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)

            # 5. Fast Vectorized Patch-level ELA computation using boxFilter
            patch_size = 32
            mean_patch = cv2.boxFilter(gray_diff, -1, (patch_size, patch_size), normalize=True)
            sq_mean_patch = cv2.boxFilter(gray_diff**2, -1, (patch_size, patch_size), normalize=True)
            var_patch = np.maximum(0.0, sq_mean_patch - (mean_patch**2))

            global_mean = float(np.mean(mean_patch))
            global_std = float(np.std(mean_patch))

            # Detect anomalous hotspot patches
            hotspots: List[List[int]] = []
            if global_std > 0.5:
                thresh_val = global_mean + (3.0 * global_std)
                mask = (mean_patch > thresh_val).astype(np.uint8)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    x, y, w_b, h_b = cv2.boundingRect(cnt)
                    if w_b >= 16 and h_b >= 16:
                        hotspots.append([int(y), int(x), int(y + h_b), int(x + w_b)])

            # Anomaly score: Splicing produces distinct localized ELA bursts rather than uniform global compression
            cv_val = (global_std / (global_mean + 1e-4)) if global_mean > 0.5 else 0.0
            anomaly_score = float(np.clip((cv_val - 0.65) / 1.5, 0.0, 1.0))

            return ForensicIndicatorResult(
                name="error_level_analysis",
                anomaly_score=round(anomaly_score, 4),
                confidence=0.92,
                details={
                    "global_mean": round(global_mean, 2),
                    "global_std": round(global_std, 2),
                    "coefficient_of_variation": round(cv_val, 3),
                    "hotspot_count": len(hotspots)
                },
                localized_hotspots=hotspots[:10]
            )
        except Exception as e:
            return ForensicIndicatorResult(
                name="error_level_analysis",
                anomaly_score=0.0,
                confidence=0.5,
                details={"exception": str(e)}
            )
