"""Module 1 OCR Engines and Adapters Package."""

from .base_engine import BaseOCREngine
from .default_engine import DefaultDocumentOCRBackend
from .easyocr_adapter import EasyOCRAdapter
from .paddleocr_adapter import PaddleOCRAdapter
from .tesseract_adapter import PyTesseractAdapter
from .test_synthetic_adapter import TestSyntheticOCRAdapter

__all__ = [
    "BaseOCREngine",
    "DefaultDocumentOCRBackend",
    "EasyOCRAdapter",
    "PaddleOCRAdapter",
    "PyTesseractAdapter",
    "TestSyntheticOCRAdapter"
]
