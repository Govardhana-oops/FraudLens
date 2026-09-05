import os
from pathlib import Path
from typing import Union, Dict, Any, Optional
import numpy as np
import cv2
import yaml
from PIL import Image
from .fusion.forensic_engine import ForensicFusionEngine
from .schemas.output_schema import TamperingReport, TamperingStatusEnum

class DocumentTamperingDetector:
    """Public high-level singleton API for Module 3 forensic analysis."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "configs" / "tampering_config.yaml")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        self.engine = ForensicFusionEngine(self.config)

    def analyze(self, image_input: Union[str, bytes, np.ndarray, Image.Image], regions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyzes an input document image and returns a structured forensic tampering report."""
        try:
            img_arr = None

            # 1. Handle string path
            if isinstance(image_input, str):
                if not os.path.exists(image_input):
                    return TamperingReport(
                        status=TamperingStatusEnum.INVALID_INPUT,
                        anomaly_score=0.0,
                        confidence=0.0,
                        errors=[f"Image file does not exist: {image_input}"],
                        review_required=True
                    ).model_dump()
                img_arr = cv2.imread(image_input)
                if img_arr is not None:
                    img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)

            # 2. Handle raw bytes
            elif isinstance(image_input, bytes):
                if len(image_input) == 0:
                    return TamperingReport(
                        status=TamperingStatusEnum.INVALID_INPUT,
                        anomaly_score=0.0,
                        confidence=0.0,
                        errors=["Received empty byte stream"],
                        review_required=True
                    ).model_dump()
                nparr = np.frombuffer(image_input, np.uint8)
                img_arr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_arr is not None:
                    img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)

            # 3. Handle PIL Image
            elif isinstance(image_input, Image.Image):
                img_arr = np.array(image_input.convert("RGB"))

            # 4. Handle numpy array
            elif isinstance(image_input, np.ndarray):
                img_arr = image_input

            # Run forensic engine
            report = self.engine.analyze(img_arr, regions=regions)
            return report.model_dump()

        except Exception as e:
            return TamperingReport(
                status=TamperingStatusEnum.PROCESSING_ERROR,
                anomaly_score=0.0,
                confidence=0.0,
                errors=[f"Unhandled exception during forensic analysis: {str(e)}"],
                review_required=True
            ).model_dump()

# Global singleton
tampering_detector = DocumentTamperingDetector()
