"""Orientation & Skew Angle Correction for Identity Documents.

Detects document rotation and text line skew using Hough Line Transform
and bounding rectangle orientation, applying affine rotation correction.
"""

import cv2
import numpy as np

class DocumentDeskewer:
    def __init__(self, max_skew_angle: float = 45.0):
        self.max_skew_angle = max_skew_angle

    def estimate_skew_angle(self, gray_np: np.ndarray) -> float:
        """Estimates skew angle in degrees using edge detection and Hough lines."""
        edges = cv2.Canny(gray_np, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
        
        if lines is None or len(lines) == 0:
            return 0.0

        angles = []
        for line in lines:
            pts = line.ravel()
            if len(pts) < 4:
                continue
            x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
            if x2 - x1 == 0:
                continue
            angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            # Focus on near-horizontal lines
            if abs(angle) < self.max_skew_angle:
                angles.append(angle)

        if not angles:
            return 0.0

        median_angle = float(np.median(angles))
        return median_angle

    def deskew(self, image_np: np.ndarray) -> tuple[np.ndarray, float]:
        """Rotates the image to align horizontally if skew is detected."""
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY) if len(image_np.shape) == 3 else image_np
        angle = self.estimate_skew_angle(gray)

        if abs(angle) < 0.5:
            return image_np, 0.0

        h, w = image_np.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new bounding dimensions
        cos = np.abs(rot_mat[0, 0])
        sin = np.abs(rot_mat[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        rot_mat[0, 2] += (new_w / 2) - center[0]
        rot_mat[1, 2] += (new_h / 2) - center[1]

        deskewed = cv2.warpAffine(image_np, rot_mat, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return deskewed, angle
