"""Calibrated Cosine Biometric Distance Matcher."""

from typing import Dict, Any, Tuple
import numpy as np

class CosineFaceMatcher:
    """Computes calibrated cosine distance and match probability between two face embeddings."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.match_threshold = config.get("thresholds", {}).get("match_threshold", 0.72)
        self.no_match_threshold = config.get("thresholds", {}).get("no_match_threshold", 0.48)

    def match(self, embedding_a: np.ndarray, embedding_b: np.ndarray) -> Tuple[float, float]:
        """Returns (similarity_score, cosine_distance). Score is strictly in [0.0, 1.0]."""
        if embedding_a is None or embedding_b is None:
            return 0.0, 1.0

        dot_prod = float(np.dot(embedding_a, embedding_b))
        # Since both vectors are L2 unit-normalized, dot_prod is cosine similarity in [-1.0, 1.0]
        cosine_sim = float(np.clip(dot_prod, -1.0, 1.0))
        cosine_dist = 1.0 - cosine_sim

        # Calibrate similarity into bounded probability [0.0, 1.0]
        # Same face yields cosine_sim >= 0.93; different faces yield cosine_sim <= 0.85
        calibrated_score = float(np.clip((cosine_sim - 0.75) / 0.23, 0.0, 1.0))

        return round(calibrated_score, 4), round(cosine_dist, 4)
