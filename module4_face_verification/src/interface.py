import os
from pathlib import Path
from typing import Union, Dict, Any, Optional
import numpy as np
import cv2
import yaml
from PIL import Image
from .pipeline.verification_engine import BiometricVerificationEngine
from .schemas.output_schema import BiometricVerificationReport, BiometricStatusEnum

class FaceVerifier:
    """Public high-level singleton API for Module 4 Biometric 1:1 Verification."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "configs" / "biometric_config.yaml")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        self.engine = BiometricVerificationEngine(self.config)

    def _load_image(self, img_input: Union[str, bytes, np.ndarray, Image.Image]) -> Optional[np.ndarray]:
        """Converts diverse image input formats into a standardized RGB numpy array."""
        if img_input is None:
            return None

        if isinstance(img_input, str):
            if not os.path.exists(img_input):
                return None
            arr = cv2.imread(img_input)
            if arr is not None:
                return cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
            return None

        if isinstance(img_input, bytes):
            if len(img_input) == 0:
                return None
            nparr = np.frombuffer(img_input, np.uint8)
            arr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if arr is not None:
                return cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
            return None

        if isinstance(img_input, Image.Image):
            return np.array(img_input.convert("RGB"))

        if isinstance(img_input, np.ndarray):
            return img_input

        return None

    def verify(self, document_image: Union[str, bytes, np.ndarray, Image.Image], live_image: Union[str, bytes, np.ndarray, Image.Image]) -> Dict[str, Any]:
        """Performs 1:1 biometric comparison between document portrait and live capture."""
        try:
            doc_arr = self._load_image(document_image)
            live_arr = self._load_image(live_image)

            if doc_arr is None or live_arr is None:
                missing = []
                if doc_arr is None:
                    missing.append("document_image")
                if live_arr is None:
                    missing.append("live_image")
                return BiometricVerificationReport(
                    status=BiometricStatusEnum.INVALID_INPUT,
                    similarity_score=0.0,
                    confidence=0.0,
                    errors=[f"Failed to load or decode input images: {', '.join(missing)}"],
                    review_required=True
                ).model_dump()

            report = self.engine.verify(doc_arr, live_arr)
            return report.model_dump()

        except Exception as e:
            return BiometricVerificationReport(
                status=BiometricStatusEnum.PROCESSING_ERROR,
                similarity_score=0.0,
                confidence=0.0,
                errors=[f"Unhandled exception during biometric verification: {str(e)}"],
                review_required=True
            ).model_dump()

# Global singleton
face_verifier = FaceVerifier()
