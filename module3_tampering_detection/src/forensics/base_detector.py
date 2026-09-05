"""Base Forensic Detector Interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
from ..schemas.output_schema import ForensicIndicatorResult

class BaseForensicDetector(ABC):
    """Abstract base class for all forensic detection modules."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def detect(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> ForensicIndicatorResult:
        """Analyzes an RGB/BGR numpy image and returns a structured ForensicIndicatorResult."""
        pass
