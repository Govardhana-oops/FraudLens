"""Comprehensive Test Suite for Pluggable Alternative OCR Engines & Adapters in Module 1."""

import os
import sys
import pytest
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from src.interface import DocumentOCR, document_ocr
from src.ocr.engine import OCREngine
from src.ocr.engines.base_engine import BaseOCREngine
from src.ocr.engines.default_engine import DefaultDocumentOCRBackend
from src.ocr.engines.easyocr_adapter import EasyOCRAdapter
from src.ocr.engines.paddleocr_adapter import PaddleOCRAdapter
from src.ocr.engines.tesseract_adapter import PyTesseractAdapter
from src.ocr.engines.test_synthetic_adapter import TestSyntheticOCRAdapter


def _create_synthetic_passport_image(doc_num="P9876543", surname="SMITH", given="JANE", nationality="CAN", dob="850101", exp="300101"):
    """Creates a high-contrast synthetic passport image with VIZ and valid TD3 MRZ."""
    img = Image.new("RGB", (800, 520), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    # Document Header
    draw.text((50, 40), "PASSPORT / PASSEPORT", fill=(10, 10, 10))
    draw.text((50, 70), "CANADA", fill=(10, 10, 10))

    # Visual Inspection Zone (VIZ)
    draw.text((50, 120), f"Passport No: {doc_num}", fill=(10, 10, 10))
    draw.text((50, 150), f"Surname: {surname}", fill=(10, 10, 10))
    draw.text((50, 180), f"Given Names: {given}", fill=(10, 10, 10))
    draw.text((50, 210), f"Nationality: {nationality}", fill=(10, 10, 10))
    draw.text((50, 240), f"Date of Birth: 01 JAN 1985", fill=(10, 10, 10))
    draw.text((50, 270), f"Date of Expiry: 01 JAN 2030", fill=(10, 10, 10))
    draw.text((50, 300), "Sex: F", fill=(10, 10, 10))

    # Photo Box placeholder
    draw.rectangle([550, 100, 720, 320], outline=(50, 50, 50), fill=(200, 200, 200), width=2)
    draw.text((600, 200), "[PHOTO]", fill=(50, 50, 50))

    # TD3 MRZ Zone (2 lines of 44 characters)
    l1 = f"P<{nationality}{surname}<<{given}".ljust(44, "<")
    l2 = f"{doc_num}<0{nationality}{dob}0F{exp}0<<<<<<<<<<<<<<<0".ljust(44, "<")

    draw.text((50, 410), l1, fill=(0, 0, 0))
    draw.text((50, 450), l2, fill=(0, 0, 0))

    return np.array(img)


# 1. Existing Module 1 Engine Tests
def test_default_engine_available_and_registers():
    engine = OCREngine()
    available = engine.get_available_engines()
    assert "default" in available
    assert "existing" in available
    assert engine.default_backend.is_available() is True


# 2. EasyOCR Adapter Tests
def test_easyocr_adapter_execution():
    adapter = EasyOCRAdapter()
    assert adapter.is_available() is True
    assert adapter.name == "easyocr_adapter"

    test_img = _create_synthetic_passport_image()
    res = adapter.recognize(test_img)
    assert isinstance(res, dict)
    assert "raw_text" in res
    assert "lines" in res
    assert "words" in res
    assert "average_confidence" in res
    assert res["engine"] == "easyocr_adapter"
    assert len(res["lines"]) > 0


# 3. PaddleOCR Adapter Tests
def test_paddleocr_adapter_graceful_handling():
    adapter = PaddleOCRAdapter()
    assert adapter.name == "paddleocr_adapter"
    # Even if paddleocr is not installed, recognize must return valid schema without crashing
    test_img = _create_synthetic_passport_image()
    res = adapter.recognize(test_img)
    assert isinstance(res, dict)
    assert "raw_text" in res
    assert "average_confidence" in res


# 4. PyTesseract Adapter Tests
def test_tesseract_adapter_graceful_handling():
    adapter = PyTesseractAdapter()
    assert adapter.name == "tesseract_adapter"
    test_img = _create_synthetic_passport_image()
    res = adapter.recognize(test_img)
    assert isinstance(res, dict)
    assert "raw_text" in res
    assert "average_confidence" in res


# 5. Engine Switching via Interface
def test_engine_switching_via_document_ocr():
    doc_ocr = DocumentOCR()
    test_img = _create_synthetic_passport_image()

    # Default engine
    res_default = doc_ocr.process(test_img, engine="default")
    assert res_default["status"] in ["SUCCESS", "REVIEW_REQUIRED"]
    assert res_default["processing_metadata"]["engine_used"] == "default_multiscale_neural"

    # EasyOCR adapter
    res_easy = doc_ocr.process(test_img, engine="easyocr")
    assert res_easy["status"] in ["SUCCESS", "REVIEW_REQUIRED"]
    assert res_easy["processing_metadata"]["engine_used"] == "easyocr_adapter"


# 6. AUTO Mode Tests
def test_auto_mode_selection():
    doc_ocr = DocumentOCR()
    test_img = _create_synthetic_passport_image()

    res = doc_ocr.process(test_img, engine="auto")
    assert res["status"] in ["SUCCESS", "REVIEW_REQUIRED"]
    assert res["processing_metadata"]["engine_used"] in ["default_multiscale_neural", "easyocr_adapter"]


# 7. OCR Failure / Invalid Input Handling
def test_invalid_image_inputs_produce_invalid_input_status():
    doc_ocr = DocumentOCR()
    
    # 0-byte input
    res_empty = doc_ocr.process(b"")
    assert res_empty["status"] == "INVALID_INPUT"
    assert res_empty["review_required"] is True

    # Low resolution image (<100x100)
    low_res = np.ones((50, 50, 3), dtype=np.uint8) * 200
    res_low = doc_ocr.process(low_res)
    assert res_low["status"] == "INVALID_INPUT"
    assert res_low["review_required"] is True


# 8. Blank Canvas Fast-Path
def test_blank_image_produces_unknown():
    doc_ocr = DocumentOCR()
    blank_img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    res = doc_ocr.process(blank_img)
    assert res["status"] in ["UNKNOWN", "REVIEW_REQUIRED"]
    assert res["review_required"] is True


# 9. Passport Field Extraction & MRZ
def test_passport_extraction_with_easyocr_engine():
    doc_ocr = DocumentOCR()
    test_img = _create_synthetic_passport_image(doc_num="P5551234", surname="DOE", given="JOHN")
    
    res = doc_ocr.process(test_img, engine="easyocr")
    assert res["document_type"]["value"] == "passport"
    assert "fields" in res
    assert res["mrz"] is not None
    assert isinstance(res["mrz"]["lines"], list)


# 10. Visual / MRZ Conflict Detection Preservation
def test_visual_mrz_conflict_preservation():
    # Passport with mismatching passport number in visual vs MRZ
    img = Image.new("RGB", (800, 520), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.text((50, 40), "PASSPORT / PASSEPORT", fill=(10, 10, 10))
    draw.text((50, 70), "CANADA", fill=(10, 10, 10))
    draw.text((50, 120), "Passport No: P1111111", fill=(10, 10, 10))  # Visual has P1111111
    draw.text((50, 150), "Surname: CONFLICT", fill=(10, 10, 10))
    
    # MRZ has P2222222
    l1 = "P<CANCONFLICT<<TEST<<<<<<<<<<<<<<<<<<<<<<<<<"
    l2 = "P2222222<0CAN8501010F3001010<<<<<<<<<<<<<<<0"
    draw.text((50, 410), l1, fill=(0, 0, 0))
    draw.text((50, 450), l2, fill=(0, 0, 0))
    
    test_img = np.array(img)
    doc_ocr = DocumentOCR()
    res = doc_ocr.process(test_img)
    
    # Conflict must be flagged or review required
    assert res["review_required"] is True


# 11. Strict Isolation of SyntheticOCREngine (Zero Hardcoded Identities in Production)
def test_synthetic_ocr_engine_strictly_isolated_from_production():
    adapter = TestSyntheticOCRAdapter(allow_test_mock=False)
    assert adapter.is_available() is False
    assert adapter.IS_TEST_ONLY is True

    # Attempting to run in production mode must raise PermissionError
    test_img = np.ones((100, 100, 3), dtype=np.uint8)
    with pytest.raises(PermissionError) as excinfo:
        adapter.recognize(test_img)
    assert "strictly forbidden in production" in str(excinfo.value)


# 12. Non-Existent Engine Selection Falls Back Gracefully
def test_nonexistent_engine_falls_back_to_default():
    doc_ocr = DocumentOCR()
    test_img = _create_synthetic_passport_image()

    res = doc_ocr.process(test_img, engine="non_existent_engine_xyz")
    assert res["status"] in ["SUCCESS", "REVIEW_REQUIRED"]
    assert res["processing_metadata"]["engine_used"] == "default_multiscale_neural"
