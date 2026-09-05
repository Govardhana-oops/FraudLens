"""Illumination Correction & Contrast Enhancement.

Applies CLAHE in LAB space and adaptive gamma adjustment to eliminate shadows
and highlight subtle document text without causing thresholding clipping.
"""

import cv2
import numpy as np

class IlluminationNormalizer:
    def __init__(self, clip_limit: float = 2.0, tile_grid_size: tuple = (8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def apply_clahe(self, image_np: np.ndarray) -> np.ndarray:
        """Applies CLAHE on the L channel of LAB color space."""
        if len(image_np.shape) == 2:
            return self.clahe.apply(image_np)

        lab = cv2.cvtColor(image_np, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)
        l_clahe = self.clahe.apply(l_chan)
        lab_merged = cv2.merge((l_clahe, a_chan, b_chan))
        return cv2.cvtColor(lab_merged, cv2.COLOR_LAB2BGR)

    def adjust_gamma(self, image_np: np.ndarray, gamma: float = 1.2) -> np.ndarray:
        """Applies gamma correction for underexposed / dark captures."""
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        return cv2.LUT(image_np, table)

    def normalize(self, image_np: np.ndarray, auto_gamma: bool = True) -> np.ndarray:
        enhanced = self.apply_clahe(image_np)
        if auto_gamma:
            # Check mean luminance to dynamically adjust gamma
            gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY) if len(enhanced.shape) == 3 else enhanced
            mean_lum = float(np.mean(gray))
            if mean_lum < 110:
                enhanced = self.adjust_gamma(enhanced, gamma=1.3)
            elif mean_lum > 210:
                enhanced = self.adjust_gamma(enhanced, gamma=0.85)
        return enhanced
