"""Public Interface for Module 2: Document Validation Engine.

Usage:
    from src.interface import document_validator
    result = document_validator.validate(module1_output_dict)
"""

import json
from typing import Union, Dict, Any, Optional
from .schemas.input_schema import Module1InputPayload
from .schemas.output_schema import DocumentValidationResult, ValidationStatusEnum
from .engine.rule_engine import RuleEngine

class DocumentValidator:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.engine = RuleEngine(self.config)
        self.module_version = "0.1.0"

    def validate(self, input_data: Union[Dict[str, Any], str, Module1InputPayload]) -> Dict[str, Any]:
        """Validates structured Module 1 OCR output and returns standardized validation report."""
        try:
            # 1. Parse and sanitize input
            if isinstance(input_data, str):
                try:
                    raw_dict = json.loads(input_data)
                except json.JSONDecodeError as jde:
                    return {
                        "module": "module2_document_validation",
                        "module_version": self.module_version,
                        "document_type": "unknown_document",
                        "overall_status": ValidationStatusEnum.INVALID_INPUT.value,
                        "validation_score": 0.0,
                        "checks": [],
                        "field_results": {},
                        "cross_field_conflicts": [],
                        "mrz_validation": None,
                        "warnings": [],
                        "errors": [f"Malformed JSON string: {str(jde)}"],
                        "review_required": True,
                        "validation_metadata": {"error_type": "JSON_DECODE_ERROR"}
                    }
            elif isinstance(input_data, dict):
                raw_dict = input_data
            elif isinstance(input_data, Module1InputPayload):
                return self.engine.validate(input_data).to_dict()
            else:
                return {
                    "module": "module2_document_validation",
                    "module_version": self.module_version,
                    "document_type": "unknown_document",
                    "overall_status": ValidationStatusEnum.INVALID_INPUT.value,
                    "validation_score": 0.0,
                    "checks": [],
                    "field_results": {},
                    "cross_field_conflicts": [],
                    "mrz_validation": None,
                    "warnings": [],
                    "errors": [f"Unsupported input type: {type(input_data)}"],
                    "review_required": True,
                    "validation_metadata": {"error_type": "INVALID_INPUT_TYPE"}
                }

            # 2. Instantiate Input Payload
            payload = Module1InputPayload.from_dict(raw_dict)

            # 3. Execute Validation Engine
            result_obj = self.engine.validate(payload)
            return result_obj.to_dict()

        except Exception as e:
            return {
                "module": "module2_document_validation",
                "module_version": self.module_version,
                "document_type": "unknown_document",
                "overall_status": ValidationStatusEnum.PROCESSING_ERROR.value,
                "validation_score": 0.0,
                "checks": [],
                "field_results": {},
                "cross_field_conflicts": [],
                "mrz_validation": None,
                "warnings": ["Internal validation exception handled safely"],
                "errors": [str(e)],
                "review_required": True,
                "validation_metadata": {"error_type": "PROCESSING_EXCEPTION"}
            }

# Global singleton
document_validator = DocumentValidator()
