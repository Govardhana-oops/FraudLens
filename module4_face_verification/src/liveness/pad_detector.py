from typing import Dict, Any, Optional
import numpy as np
import cv2
from ..schemas.output_schema import LivenessAssessment

class PresentationAttackDetector:
    """Evaluates live capture frames for presentation attack signatures (screen replay, paper masks)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_liveness = config.get("thresholds", {}).get("min_liveness_score", 0.65)

    def assess_liveness(self, image: np.ndarray, face_crop: Optional[np.ndarray]) -> LivenessAssessment:
        if image is None or face_crop is None or face_crop.size == 0:
            return LivenessAssessment(
                is_live=False,
                liveness_score=0.0,
                attack_type_detected="no_valid_face_to_analyze",
                warnings=["Cannot perform liveness check on empty face crop"]
            )

        warnings = []
        attack_detected = None

        # 1. 2D FFT High-frequency periodic screen lattice / moiré check
        target_size = 128
        resized_crop = cv2.resize(face_crop, (target_size, target_size), interpolation=cv2.INTER_AREA)
        dft = np.fft.fft2(resized_crop.astype(np.float32))
        dft_shift = np.fft.fftshift(dft)
        mag = 20 * np.log(np.abs(dft_shift) + 1.0)

        # Mask DC
        cy, cx = target_size // 2, target_size // 2
        y, x = np.ogrid[:target_size, :target_size]
        mask = (x - cx)**2 + (y - cy)**2 <= 100
        mag[mask] = 0.0

        high_std = float(np.std(mag[~mask]))
        high_max = float(np.max(mag[~mask]))
        peak_prom = (high_max - float(np.mean(mag[~mask]))) / (high_std + 1e-4)

        # 2. Texture Energy / Local Binary Pattern Discontinuity
        lap = cv2.Laplacian(resized_crop, cv2.CV_64F)
        texture_energy = float(np.mean(np.abs(lap)))

        # Screen replay exhibits unnatural isolated high-frequency spectral spikes (peak_prom > 4.5)
        if peak_prom > 4.8:
            attack_detected = "screen_replay_moire_pattern"
            warnings.append("High-frequency periodic moiré pattern detected")
            liveness_score = 0.20
        elif texture_energy < 0.5:
            attack_detected = "printed_paper_smoothing"
            warnings.append("Abnormally flat skin texture detected")
            liveness_score = 0.40
        else:
            liveness_score = 0.95

        is_live = (liveness_score >= self.min_liveness)

        return LivenessAssessment(
            is_live=is_live,
            liveness_score=round(liveness_score, 3),
            attack_type_detected=attack_detected,
            warnings=warnings
        )
