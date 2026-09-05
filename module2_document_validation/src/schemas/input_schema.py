"""Input Schema Definition for Module 2 Document Validation.

Validates the incoming JSON structure produced by Module 1 OCR.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class Module1StatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_DOCUMENT = "UNSUPPORTED_DOCUMENT"
    PROCESSING_ERROR = "PROCESSING_ERROR"

@dataclass
class Module1DocumentType:
    value: str
    confidence: float = 1.0

@dataclass
class Module1Field:
    value: str
    raw_value: str = ""
    confidence: float = 1.0
    status: str = "VALID"
    source: str = "visual_text"
    extraction_method: str = "spatial_label_value"
    warnings: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)

@dataclass
class Module1MRZ:
    status: str
    mrz_format: str
    lines: List[str]
    checksum_valid: bool
    checks: Dict[str, bool] = field(default_factory=dict)

@dataclass
class Module1Conflict:
    field: str
    status: str
    visual_value: str
    mrz_value: str
    confidence_visual: float = 0.0
    confidence_mrz: float = 0.0
    resolution_recommendation: str = "REVIEW_REQUIRED"

@dataclass
class Module1InputPayload:
    status: str
    document_type: Module1DocumentType
    fields: Dict[str, Module1Field] = field(default_factory=dict)
    mrz: Optional[Module1MRZ] = None
    consistency: Dict[str, Any] = field(default_factory=dict)
    review_required: bool = False
    warnings: List[str] = field(default_factory=list)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Module1InputPayload":
        """Safely instantiates payload from raw dictionary with strict validation."""
        if not isinstance(data, dict):
            raise ValueError("Input payload must be a dictionary")

        status_val = data.get("status", "PROCESSING_ERROR")
        
        # Document type handling
        dt_raw = data.get("document_type", {})
        if isinstance(dt_raw, dict):
            dt_obj = Module1DocumentType(
                value=str(dt_raw.get("value", "unknown_document")),
                confidence=float(dt_raw.get("confidence", 0.0))
            )
        else:
            dt_obj = Module1DocumentType(value=str(dt_raw), confidence=1.0)

        # Fields handling
        fields_dict = {}
        for k, v in data.get("fields", {}).items():
            if isinstance(v, dict):
                val_raw = v.get("value")
                raw_val_raw = v.get("raw_value")
                val_str = str(val_raw) if (val_raw is not None and str(val_raw).upper() not in ["NONE", "NULL"]) else ""
                raw_val_str = str(raw_val_raw) if raw_val_raw is not None else val_str
                fields_dict[k] = Module1Field(
                    value=val_str,
                    raw_value=raw_val_str,
                    confidence=float(v.get("confidence", 1.0)),
                    status=str(v.get("status", "VALID")),
                    source=str(v.get("source", "visual_text")),
                    extraction_method=str(v.get("extraction_method", "spatial_label_value")),
                    warnings=list(v.get("warnings", [])),
                    corrections=list(v.get("corrections", []))
                )
            elif v is None:
                fields_dict[k] = Module1Field(value="")
            else:
                fields_dict[k] = Module1Field(value=str(v) if str(v).upper() not in ["NONE", "NULL"] else "")

        # MRZ handling
        mrz_obj = None
        mrz_raw = data.get("mrz")
        if isinstance(mrz_raw, dict):
            mrz_obj = Module1MRZ(
                status=str(mrz_raw.get("status", "UNKNOWN")),
                mrz_format=str(mrz_raw.get("mrz_format", "UNKNOWN")),
                lines=list(mrz_raw.get("lines", [])),
                checksum_valid=bool(mrz_raw.get("checksum_valid", False)),
                checks=dict(mrz_raw.get("checks", {}))
            )

        return cls(
            status=status_val,
            document_type=dt_obj,
            fields=fields_dict,
            mrz=mrz_obj,
            consistency=data.get("consistency", {}),
            review_required=bool(data.get("review_required", False)),
            warnings=list(data.get("warnings", [])),
            processing_metadata=dict(data.get("processing_metadata", {})),
            error_details=data.get("error_details")
        )
