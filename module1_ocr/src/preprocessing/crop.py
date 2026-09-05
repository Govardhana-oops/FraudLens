"""Document Boundary Detection & 4-Point Perspective Transform.

Identifies the outer quadrilateral contour of an identity document and
applies perspective correction to produce a standardized frontal view.
"""

import cv2
import numpy as np

class DocumentCropper:
    def __init__(self, min_area_ratio: float = 0.20):
        self.min_area_ratio = min_area_ratio

    def order_points(self, pts: np.ndarray) -> np.ndarray:
        """Orders coordinates: top-left, top-right, bottom-right, bottom-left."""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def find_document_contour(self, image_np: np.ndarray) -> np.ndarray | None:
        """Detects the largest 4-point quadrilateral contour."""
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY) if len(image_np.shape) == 3 else image_np
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 30, 120)

        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        total_area = image_np.shape[0] * image_np.shape[1]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4 and cv2.contourArea(approx) > (self.min_area_ratio * total_area):
                return approx.reshape(4, 2)

        return None

    def perspective_crop(self, image_np: np.ndarray) -> tuple[np.ndarray, bool]:
        """Applies 4-point perspective warp if document boundary is found."""
        pts = self.find_document_contour(image_np)
        if pts is None:
            return image_np, False

        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # Calculate width of new image
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_w = max(int(width_a), int(width_b))

        # Calculate height of new image
        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_h = max(int(height_a), int(height_b))

        dst = np.array([
            [0, 0],
            [max_w - 1, 0],
            [max_w - 1, max_h - 1],
            [0, max_h - 1]
        ], dtype="float32")

        m = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image_np, m, (max_w, max_h))
        return warped, True
