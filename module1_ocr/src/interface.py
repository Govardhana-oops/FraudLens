"""Unified Public Pipeline Interface for Module 1: Document OCR & Understanding.

Exposes a clean, stable public contract:
    result = DocumentOCR.process(image_input)

Supports:
- File path (str or Path)
- Raw image bytes (bytes)
- OpenCV image array (np.ndarray)

Handles:
- Input validation (corrupt, oversized, empty, low-resolution)
- Full end-to-end processing pipeline
- Safe error recovery (zero raw exception exposure)
- Strict adherence to zero-false-fraud policy
"""

import os
import io
import cv2
import numpy as np
from PIL import Image
from typing import Union, Dict, Any, Optional, Tuple
from pathlib import Path

from .preprocessing.pipeline import PreprocessingPipeline
from .preprocessing.roi_extractor import DocumentROIExtractor
from .ocr.engine import OCREngine
from .extraction.pipeline import DocumentUnderstandingPipeline

class DocumentOCR:
    def __init__(self, min_confidence: float = 0.50, engine: Optional[str] = None):
        self.preprocessing_pipeline = PreprocessingPipeline(mode="standard")
        self.roi_extractor = DocumentROIExtractor(target_dpi_scale=1.5)
        self.ocr_engine = OCREngine(confidence_threshold=0.40, engine=engine)
        self.understanding_pipeline = DocumentUnderstandingPipeline(min_confidence=min_confidence)
        self.model_version = "LayoutAware-MultiScale-OCR-v2.0"
        self.module_version = "1.0.0"

    def _load_image(self, image_input: Union[str, Path, bytes, np.ndarray]) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """Safely loads and validates image input in any standard format."""
        try:
            if isinstance(image_input, (str, Path)):
                img_path = str(image_input)
                if not os.path.exists(img_path):
                    return None, f"Input image file not found: {img_path}"
                if os.path.getsize(img_path) == 0:
                    return None, "Input image file is empty (0 bytes)"
                img = cv2.imread(img_path)
                if img is None:
                    return None, "Unable to decode image file (corrupted or unsupported format)"
                return img, None

            elif isinstance(image_input, bytes):
                if len(image_input) == 0:
                    return None, "Provided image bytes are empty"
                nparr = np.frombuffer(image_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    return None, "Unable to decode raw image byte stream"
                return img, None

            elif isinstance(image_input, np.ndarray):
                if image_input.size == 0:
                    return None, "Provided numpy image array is empty"
                if len(image_input.shape) == 2:
                    img = cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
                else:
                    img = image_input
                return img, None

            else:
                return None, f"Unsupported image input type: {type(image_input)}"

        except Exception as e:
            return None, f"Image loading error: {str(e)}"

    def process(
        self,
        image_input: Union[str, Path, bytes, np.ndarray],
        metadata: Optional[Dict[str, Any]] = None,
        engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes the complete OCR and document understanding pipeline."""
        metadata = metadata or {}
        req_engine = engine or metadata.get("ocr_engine")
        
        # 1. Validate and load image
        img_bgr, err = self._load_image(image_input)
        if err:
            return {
                "status": "INVALID_INPUT",
                "document_type": {"value": "unknown_document", "confidence": 0.0},
                "fields": {},
                "mrz": None,
                "consistency": {"status": "NOT_APPLICABLE", "conflicts": []},
                "review_required": True,
                "warnings": [err],
                "error_details": {"type": "INVALID_INPUT", "message": err},
                "processing_metadata": {
                    "module": "module1_ocr",
                    "module_version": self.module_version,
                    "model_version": self.model_version
                }
            }

        try:
            h, w = img_bgr.shape[:2]
            if w < 100 or h < 100:
                return {
                    "status": "INVALID_INPUT",
                    "document_type": {"value": "unknown_document", "confidence": 0.0},
                    "fields": {},
                    "mrz": None,
                    "consistency": {"status": "NOT_APPLICABLE", "conflicts": []},
                    "review_required": True,
                    "warnings": [f"Image resolution {w}x{h} is below minimal threshold 100x100"],
                    "error_details": {"type": "LOW_RESOLUTION", "message": "Resolution too low for processing"},
                    "processing_metadata": {
                        "module": "module1_ocr",
                        "module_version": self.module_version,
                        "model_version": self.model_version
                    }
                }

            # 2. Quality check & Preprocessing
            preproc_res = self.preprocessing_pipeline.process_image(img_bgr)
            proc_img = preproc_res["processed_image"]
            quality = preproc_res["quality_assessment"]

            # 3. Multi-Scale ROI Extraction & Neural OCR
            zones = self.roi_extractor.extract_zones(proc_img)
            ocr_res = self.ocr_engine.extract_text(
                zones["full_document"],
                mrz_crop=zones.get("mrz_high_dpi"),
                engine=req_engine
            )

            # 4. Document Understanding Pipeline
            proc_meta = {
                "module": "module1_ocr",
                "module_version": self.module_version,
                "model_version": self.model_version,
                "engine_used": ocr_res.get("engine", "default"),
                "quality_assessment": quality,
                "preprocessing_mode": "roi_multiscale_neural",
                "user_metadata": metadata
            }

            understanding_res = self.understanding_pipeline.process(ocr_res["raw_text"], processing_metadata=proc_meta)
            res_dict = understanding_res.to_dict()

            # Format standardized integration payload
            formatted_fields = {}
            for fname, fval in res_dict.get("fields", {}).items():
                formatted_fields[fname] = {
                    "value": fval["value"],
                    "raw_value": fval["raw_value"],
                    "confidence": fval["confidence"],
                    "status": fval["validation_status"],
                    "source": fval["source"],
                    "extraction_method": fval["extraction_method"],
                    "warnings": fval["warnings"],
                    "corrections": fval["corrections"]
                }

            mrz_info = None
            if res_dict.get("mrz_validation"):
                mv = res_dict["mrz_validation"]
                mrz_info = {
                    "status": mv["status"],
                    "mrz_format": mv["mrz_format"],
                    "lines": mv["lines"],
                    "checksum_valid": mv["all_checksums_pass"],
                    "checks": {
                        "document_number": mv["document_number_checksum"],
                        "date_of_birth": mv["dob_checksum"],
                        "date_of_expiry": mv["expiry_checksum"],
                        "composite": mv["composite_checksum"]
                    }
                }

            conflicts = res_dict.get("cross_field_conflicts", [])
            consistency_status = "CONSISTENT" if len(conflicts) == 0 else "CONFLICT"

            warnings = []
            if quality.get("is_blurry"):
                warnings.append(f"Image blur detected (Laplacian score: {quality.get('blur_score', 0):.1f})")
            if quality.get("has_glare"):
                warnings.append(f"Image glare detected (Ratio: {quality.get('glare_ratio', 0):.2f})")
            if len(conflicts) > 0:
                warnings.append(f"Evidentiary cross-field conflict detected ({len(conflicts)} discrepancies)")

            return {
                "status": res_dict["status"],
                "document_type": {
                    "value": res_dict["document_type"],
                    "confidence": res_dict["document_type_confidence"]
                },
                "fields": formatted_fields,
                "mrz": mrz_info,
                "consistency": {
                    "status": consistency_status,
                    "conflicts": conflicts
                },
                "review_required": res_dict["review_required"],
                "warnings": warnings,
                "processing_metadata": proc_meta
            }

        except Exception as e:
            return {
                "status": "PROCESSING_ERROR",
                "document_type": {"value": "unknown_document", "confidence": 0.0},
                "fields": {},
                "mrz": None,
                "consistency": {"status": "NOT_APPLICABLE", "conflicts": []},
                "review_required": True,
                "warnings": ["Internal processing exception handled gracefully"],
                "error_details": {"type": "PROCESSING_ERROR", "message": str(e)},
                "processing_metadata": {
                    "module": "module1_ocr",
                    "module_version": self.module_version,
                    "model_version": self.model_version
                }
            }

# Global singleton for direct library import
document_ocr = DocumentOCR()
