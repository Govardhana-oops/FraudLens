"""Edge & Gradient Discontinuity Forensic Detector."""

from typing import Dict, Any, Optional, List
import numpy as np
import cv2
from .base_detector import BaseForensicDetector
from ..schemas.output_schema import ForensicIndicatorResult

class EdgeGradientDetector(BaseForensicDetector):
    """Detects artificial border clipping, sharp gradient discontinuities, and copy-paste boundaries."""

    def detect(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> ForensicIndicatorResult:
        if image is None or image.size == 0:
            return ForensicIndicatorResult(
                name="edge_gradient_discontinuity",
                anomaly_score=0.0,
                confidence=0.0,
                details={"error": "Empty image buffer"}
            )

        try:
            # 1. Convert to grayscale & scale to standard processing resolution
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

            # 2. Compute Sobel gradients in X and Y directions
            sobelx = cv2.Sobel(gray_proc, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray_proc, cv2.CV_64F, 0, 1, ksize=3)
            magnitude = np.sqrt(sobelx**2 + sobely**2)

            # 3. Detect unnatural rectangular edge boundaries
            edges = cv2.Canny(gray_proc, 100, 200)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=70, minLineLength=30, maxLineGap=5)

            rectangular_discontinuities = 0
            hotspots: List[List[int]] = []

            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # Check for purely axis-aligned artificial lines in inner regions (not image borders)
                    is_horizontal = abs(y1 - y2) < 2 and 20 < y1 < gray.shape[0] - 20
                    is_vertical = abs(x1 - x2) < 2 and 20 < x1 < gray.shape[1] - 20
                    if is_horizontal or is_vertical:
                        # Check gradient sharpness across this line
                        grad_strength = np.mean(magnitude[min(y1, y2):max(y1, y2)+1, min(x1, x2):max(x1, x2)+1])
                        if grad_strength > 120.0:
                            rectangular_discontinuities += 1
                            hotspots.append([int(min(y1, y2)), int(min(x1, x2)), int(max(y1, y2)+2), int(max(x1, x2)+2)])

            # Anomaly score based on unnatural straight gradient jumps
            anomaly_score = float(np.clip(rectangular_discontinuities / 8.0, 0.0, 1.0))

            return ForensicIndicatorResult(
                name="edge_gradient_discontinuity",
                anomaly_score=round(anomaly_score, 4),
                confidence=0.88,
                details={
                    "rectangular_discontinuities": rectangular_discontinuities,
                    "mean_gradient_magnitude": round(float(np.mean(magnitude)), 2),
                    "hotspot_count": len(hotspots)
                },
                localized_hotspots=hotspots[:10]
            )
        except Exception as e:
            return ForensicIndicatorResult(
                name="edge_gradient_discontinuity",
                anomaly_score=0.0,
                confidence=0.5,
                details={"exception": str(e)}
            )
