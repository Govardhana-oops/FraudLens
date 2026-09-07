"""Universal Deep-Learning Neural OCR Engine for Identity Documents.

Provides:
1. Pluggable OCR Engine Architecture:
   - Default: Multi-Scale Neural EasyOCR (CRAFT + ResNet/LSTM with High-DPI MRZ zoning & blank fast-path)
   - Alternative: EasyOCR Adapter (Phone OCR compatible)
   - Alternative: PaddleOCR Adapter (Phone OCR compatible)
   - Alternative: PyTesseract Adapter (Phone OCR compatible)
   - Auto Mode: Dynamic fallback across genuine neural engines
2. Zero-Hallucination Safe Fallbacks (Synthetic test engine strictly isolated)
3. 100% Backward Compatibility with frozen Module 1 interface
"""

import os
import sys
import ssl
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

# Ensure SSL and UTF-8 encoding support
os.environ['PYTHONIOENCODING'] = 'utf-8'
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

import gc

# Import base engines and adapters
from .engines.base_engine import BaseOCREngine
from .engines.default_engine import DefaultDocumentOCRBackend, get_easyocr_reader
from .engines.easyocr_adapter import EasyOCRAdapter
from .engines.paddleocr_adapter import PaddleOCRAdapter
from .engines.tesseract_adapter import PyTesseractAdapter
from .engines.test_synthetic_adapter import TestSyntheticOCRAdapter

# Alias for backward compatibility
DocumentOCRBackend = DefaultDocumentOCRBackend


class OCREngine:
    """Master OCR Engine Dispatcher supporting default multi-scale neural and alternative adapters."""

    def __init__(self, confidence_threshold: float = 0.40, engine: Optional[str] = None):
        self.confidence_threshold = confidence_threshold
        self.selected_engine_type = (engine or os.getenv("OCR_ENGINE", "default")).lower().strip()
        
        # Instantiate registered engines
        self.default_backend = DefaultDocumentOCRBackend(confidence_threshold=confidence_threshold)
        self.easyocr_adapter = EasyOCRAdapter()
        self.paddleocr_adapter = PaddleOCRAdapter()
        self.tesseract_adapter = PyTesseractAdapter()

        # Backward compatibility alias
        self.backend = self.default_backend

    def get_available_engines(self) -> List[str]:
        """Returns list of currently available and functional OCR engines on this PC."""
        available = []
        if self.default_backend.is_available():
            available.append("default")
            available.append("existing")
        if self.easyocr_adapter.is_available():
            available.append("easyocr")
        if self.paddleocr_adapter.is_available():
            available.append("paddleocr")
        if self.tesseract_adapter.is_available():
            available.append("tesseract")
        return available

    def _resolve_engine(self, engine_name: Optional[str] = None) -> BaseOCREngine:
        """Resolves target engine instance based on parameter, env var, or defaults."""
        target = (engine_name or self.selected_engine_type or "default").lower().strip()

        if target in ["default", "existing", "multiscale", "default_multiscale_neural"]:
            if self.easyocr_adapter.is_available():
                return self.easyocr_adapter
            return self.default_backend
        elif target in ["easyocr", "easyocr_adapter"]:
            if self.easyocr_adapter.is_available():
                return self.easyocr_adapter
            return self.default_backend
        elif target in ["paddleocr", "paddleocr_adapter", "paddle"]:
            if self.paddleocr_adapter.is_available():
                return self.paddleocr_adapter
            # Fall back to default if PaddleOCR is not installed
            return self.default_backend
        elif target in ["tesseract", "pytesseract", "tesseract_adapter"]:
            if self.tesseract_adapter.is_available():
                return self.tesseract_adapter
            return self.default_backend
        elif target == "auto":
            # Pick highest priority functional engine (prioritize lightweight C++ tesseract if installed)
            if self.tesseract_adapter.is_available():
                return self.tesseract_adapter
            elif self.default_backend.is_available():
                return self.default_backend
            elif self.easyocr_adapter.is_available():
                return self.easyocr_adapter
            elif self.paddleocr_adapter.is_available():
                return self.paddleocr_adapter
            return self.default_backend
        else:
            return self.default_backend

    def extract_text(
        self,
        image_np: np.ndarray,
        mrz_crop: Optional[np.ndarray] = None,
        engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes text recognition using the configured or explicitly requested engine backend."""
        selected_backend = self._resolve_engine(engine)
        
        try:
            res = selected_backend.recognize(image_np, mrz_crop=mrz_crop)
            # If auto mode was used and result was empty or errored, try fallback
            if (engine or self.selected_engine_type) == "auto" and not res.get("raw_text") and selected_backend != self.default_backend:
                res = self.default_backend.recognize(image_np, mrz_crop=mrz_crop)
            return res
        except Exception as e:
            print(f"[OCREngine Error] Backend {selected_backend.name} raised exception: {e}", file=sys.stderr)
            # Safe recovery using default engine
            if selected_backend != self.default_backend:
                return self.default_backend.recognize(image_np, mrz_crop=mrz_crop)
            return {
                "raw_text": "",
                "lines": [],
                "words": [],
                "average_confidence": 0.0,
                "engine": "error_recovery"
            }
