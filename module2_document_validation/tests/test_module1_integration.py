"""Integration Test between Frozen Module 1 OCR and Module 2 Document Validation."""

import os
import sys
import pytest

# Add paths for both modules
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE1_PATH = os.path.join(WORKSPACE_ROOT, "module1_ocr")
sys.path.insert(0, WORKSPACE_ROOT)
sys.path.insert(0, MODULE1_PATH)

from module1_ocr.src.interface import document_ocr
from src.interface import document_validator

def test_module1_to_module2_direct_pipeline_integration():
    sample_img_path = os.path.join(MODULE1_PATH, "data", "cleaned", "DOC_PASSPORT_0001_v1.png")
    if not os.path.exists(sample_img_path):
        pytest.skip(f"Sample image not found: {sample_img_path}")

    # 1. Execute frozen Module 1 OCR
    m1_result = document_ocr.process(sample_img_path)
    assert "status" in m1_result
    assert "document_type" in m1_result
    assert "fields" in m1_result

    # 2. Ingest directly into Module 2 Validation Engine
    m2_result = document_validator.validate(m1_result)
    assert m2_result["module"] == "module2_document_validation"
    assert "overall_status" in m2_result
    assert "validation_score" in m2_result
    assert "checks" in m2_result
    assert "field_results" in m2_result
    assert "review_required" in m2_result
    assert m2_result["overall_status"] not in ["FRAUD", "CRIMINAL"]
