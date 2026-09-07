"""Discriminative Facial Feature Extractor."""

from typing import Dict, Any, Optional
import numpy as np
import cv2

class FaceFeatureExtractor:
    """Extracts a normalized, highly discriminative 128D facial representation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target_size = config.get("feature_extractor", {}).get("alignment_target_size", 160)
        self.embedding_dim = config.get("feature_extractor", {}).get("embedding_dimensions", 128)

    def extract(self, face_crop: np.ndarray) -> np.ndarray:
        """Extracts a normalized, highly discriminative 128D facial representation (64D High-Freq DCT + 64D Relative Spatial Profile)."""
        if face_crop is None or face_crop.size == 0:
            return np.zeros((self.embedding_dim,), dtype=np.float32)

        # 1. Standardize face crop dimensions and convert to equalized grayscale
        aligned = cv2.resize(face_crop, (128, 128), interpolation=cv2.INTER_AREA)
        if len(aligned.shape) == 3:
            gray = cv2.cvtColor(aligned, cv2.COLOR_RGB2GRAY)
        else:
            gray = aligned

        # Histogram equalization for illumination and contrast invariance
        eq = cv2.equalizeHist(gray).astype(np.float32)

        # 2. High-frequency 2D DCT (skip lowest 4 frequency bands capturing generic oval contours)
        dct = cv2.dct(eq)
        coords = []
        for s in range(3, 24):
            for y in range(s + 1):
                x = s - y
                if x < 128 and y < 128:
                    coords.append((y, x))
        dct_v = np.array([float(dct[y, x]) for y, x in coords[:64]], dtype=np.float32)
        dct_v = (dct_v - float(np.mean(dct_v))) / (float(np.linalg.norm(dct_v)) + 1e-5)

        # 3. 8x8 Spatial relative luminance differences
        patches = []
        bs = 16
        g_mean = float(np.mean(eq))
        g_std = float(np.std(eq)) + 1e-5
        for py in range(8):
            for px in range(8):
                p = eq[py*bs:(py+1)*bs, px*bs:(px+1)*bs]
                patches.append((float(np.mean(p)) - g_mean) / g_std)
        sp_v = np.array(patches, dtype=np.float32)
        sp_v = (sp_v - float(np.mean(sp_v))) / (float(np.linalg.norm(sp_v)) + 1e-5)

        # 4. Fuse into 128D embedding vector
        fused = np.concatenate([dct_v, sp_v])
        fused = fused - float(np.mean(fused))
        fused_norm = float(np.linalg.norm(fused))
        if fused_norm > 1e-6:
            fused = fused / fused_norm
        else:
            fused = np.zeros((self.embedding_dim,), dtype=np.float32)

        return fused.astype(np.float32)
