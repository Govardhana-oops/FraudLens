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
        """Extracts a 128D unit-normalized feature vector from an aligned face crop."""
        if face_crop is None or face_crop.size == 0:
            return np.zeros((self.embedding_dim,), dtype=np.float32)

        # 1. Standardize face crop dimensions
        aligned = cv2.resize(face_crop, (self.target_size, self.target_size), interpolation=cv2.INTER_AREA)

        # 2. Multi-scale gradient orientations (HOG spatial grids)
        # 4x4 spatial blocks -> 16 regions * 6 orientation bins = 96 dimensions
        gx = cv2.Sobel(aligned.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(aligned.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)

        block_size = self.target_size // 4
        histograms = []

        for by in range(4):
            for bx in range(4):
                block_mag = mag[by*block_size:(by+1)*block_size, bx*block_size:(bx+1)*block_size]
                block_ang = angle[by*block_size:(by+1)*block_size, bx*block_size:(bx+1)*block_size]

                # 6 orientation bins
                hist, _ = np.histogram(block_ang, bins=6, range=(0, 360), weights=block_mag)
                histograms.extend(hist)

        # 3. Spatial luminance & morphology profile (32 dimensions)
        # 4 horizontal strips * 4 vertical strips mean + std = 32 dimensions
        strip_h = self.target_size // 4
        strip_w = self.target_size // 4
        spatial_profile = []
        for sy in range(4):
            for sx in range(4):
                patch = aligned[sy*strip_h:(sy+1)*strip_h, sx*strip_w:(sx+1)*strip_w]
                spatial_profile.append(float(np.mean(patch)))
                spatial_profile.append(float(np.std(patch)))

        # 4. Combine into 128D embedding vector
        all_features = list(histograms) + list(spatial_profile)
        feat_vector = np.array(all_features[:self.embedding_dim], dtype=np.float32)

        # 5. L2 Unit Normalization
        norm = np.linalg.norm(feat_vector)
        if norm > 1e-6:
            feat_vector = feat_vector / norm
        else:
            feat_vector = np.zeros_like(feat_vector)

        return feat_vector
