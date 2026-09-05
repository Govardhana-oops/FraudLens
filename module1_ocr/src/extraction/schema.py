"""Standardized Output Schemas for Module 1 OCR & Document Understanding.

Stage 5 Enhanced Specification adhering to ICAO Doc 9303 & AAMVA Standards.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import json

@dataclass
class FieldCorrection:
    position: int
    from_char: str
    to_char: str
    reason: str

@dataclass
class ExtractedField:
    value: str
    raw_value: str = ""
    confidence: float = 1.0
    source: str = "visual_ocr"  # visual_ocr, mrz, barcode_pdf417, derived, cross_fused
    extraction_method: str = "spatial_label_value"  # spatial_label_value, mrz_checksum_verified, regex_pattern, layout_anchor
    validation_status: str = "VALID"  # VALID, INVALID, EXTRACTED, UNKNOWN, REVIEW_REQUIRED, NOT_APPLICABLE
    status: Optional[str] = None
    bounding_box: Optional[List[int]] = None
    warnings: List[str] = field(default_factory=list)
    corrections: List[Dict[str, Any]] = field(default_factory=list)
    is_valid: Optional[bool] = None

    def __post_init__(self):
        if not self.raw_value:
            self.raw_value = self.value
        if self.status is not None:
            self.validation_status = self.status
        elif self.is_valid is not None:
            self.validation_status = "VALID" if self.is_valid else "INVALID"
        self.status = self.validation_status

@dataclass
class CrossFieldConflict:
    field: str
    status: str  # CONFLICT, WARNING, MATCH
    visual_value: Optional[str]
    mrz_value: Optional[str]
    confidence_visual: float
    confidence_mrz: float
    resolution_recommendation: str = "REVIEW_REQUIRED"

@dataclass
class MRZValidationResult:
    mrz_format: str  # TD1, TD2, TD3, MRV_A, MRV_B
    lines: List[str]
    document_number_checksum: bool
    dob_checksum: bool
    expiry_checksum: bool
    composite_checksum: bool
    all_checksums_pass: bool
    status: str  # VALID, CHECKSUM_FAILED, MALFORMED, NOT_PRESENT

@dataclass
class ValidationSummary:
    all_valid: bool
    valid_fields_count: int
    invalid_fields_count: int
    unknown_fields_count: int
    conflict_fields_count: int

@dataclass
class DocumentExtractionResult:
    document_type: str
    raw_text: str
    document_type_confidence: float = 1.0
    fields: Dict[str, ExtractedField] = field(default_factory=dict)
    mrz_validation: Optional[MRZValidationResult] = None
    cross_field_conflicts: List[CrossFieldConflict] = field(default_factory=list)
    validation_summary: Optional[ValidationSummary] = None
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "SUCCESS"  # SUCCESS, PARTIAL, REVIEW_REQUIRED, UNKNOWN
    review_required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serializes dataclass hierarchy into a clean dictionary."""
        res = {
            "document_type": self.document_type,
            "document_type_confidence": round(self.document_type_confidence, 3),
            "raw_text": self.raw_text,
            "fields": {
                k: {
                    "value": v.value,
                    "raw_value": v.raw_value,
                    "confidence": round(v.confidence, 3),
                    "source": v.source,
                    "extraction_method": v.extraction_method,
                    "validation_status": v.validation_status,
                    "bounding_box": v.bounding_box,
                    "warnings": v.warnings,
                    "corrections": v.corrections
                }
                for k, v in self.fields.items()
            },
            "mrz_validation": asdict(self.mrz_validation) if self.mrz_validation else None,
            "cross_field_conflicts": [asdict(c) for c in self.cross_field_conflicts],
            "validation_summary": asdict(self.validation_summary) if self.validation_summary else None,
            "processing_metadata": self.processing_metadata,
            "status": self.status,
            "review_required": self.review_required
        }
        return res

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
