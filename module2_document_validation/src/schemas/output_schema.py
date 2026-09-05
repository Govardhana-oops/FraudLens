"""Output Schema Definition for Module 2 Document Validation.

Standardized structured validation report adhering to AI-DIDSS contracts.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

class ValidationStatusEnum(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    INVALID_INPUT = "INVALID_INPUT"
    UNSUPPORTED_DOCUMENT = "UNSUPPORTED_DOCUMENT"
    PROCESSING_ERROR = "PROCESSING_ERROR"

class RuleSeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class RuleCategoryEnum(str, Enum):
    SCHEMA = "SCHEMA"
    FORMAT = "FORMAT"
    DATE = "DATE"
    CHRONOLOGY = "CHRONOLOGY"
    MRZ = "MRZ"
    CONSISTENCY = "CONSISTENCY"
    DOMAIN = "DOMAIN"

@dataclass
class ValidationCheckResult:
    rule_id: str
    category: str
    status: str            # "PASS", "FAIL", "WARNING", "UNKNOWN", "NOT_APPLICABLE"
    severity: str          # "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
    message: str
    field_name: Optional[str] = None
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FieldValidationResult:
    field_name: str
    value: Optional[str]
    status: str            # "VALID", "INVALID", "EXPIRED", "MISSING", "UNKNOWN"
    checks_passed: int = 0
    checks_failed: int = 0
    messages: List[str] = field(default_factory=list)

@dataclass
class DocumentValidationResult:
    module: str = "module2_document_validation"
    module_version: str = "0.1.0"
    document_type: str = "unknown_document"
    overall_status: str = "UNKNOWN"
    validation_score: float = 0.0
    checks: List[ValidationCheckResult] = field(default_factory=list)
    field_results: Dict[str, FieldValidationResult] = field(default_factory=dict)
    cross_field_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    mrz_validation: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    review_required: bool = False
    validation_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts object to standardized JSON-serializable dictionary."""
        return {
            "module": self.module,
            "module_version": self.module_version,
            "document_type": self.document_type,
            "overall_status": self.overall_status,
            "validation_score": round(self.validation_score, 4),
            "checks": [asdict(c) for c in self.checks],
            "field_results": {k: asdict(v) for k, v in self.field_results.items()},
            "cross_field_conflicts": self.cross_field_conflicts,
            "mrz_validation": self.mrz_validation,
            "warnings": self.warnings,
            "errors": self.errors,
            "review_required": self.review_required,
            "validation_metadata": self.validation_metadata
        }
