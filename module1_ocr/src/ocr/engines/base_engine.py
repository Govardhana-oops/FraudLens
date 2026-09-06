"""Base Abstract OCR Engine Interface for Module 1."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import numpy as np

class BaseOCREngine(ABC):
    """Abstract base class for all pluggable OCR engine backends in Module 1."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the OCR engine backend."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the engine's dependencies are installed and accessible on this system."""
        pass

    @abstractmethod
    def recognize(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Executes OCR extraction on an image numpy array.
        
        Returns a standardized dictionary:
        {
            "raw_text": str,
            "lines": List[str],
            "words": List[Dict[str, Any]],  # each item: {"text": str, "confidence": float, "bbox": [x1, y1, x2, y2]}
            "average_confidence": float,     # 0.0 to 1.0
            "engine": str                    # engine name
        }
        """
        pass
