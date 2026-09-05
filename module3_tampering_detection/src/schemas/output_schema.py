"""Output Schema and Status Taxonomy for Module 3 Tampering Detection."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TamperingStatusEnum(str, Enum):
    NO_TAMPERING_EVIDENCE = "NO_TAMPERING_EVIDENCE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    POTENTIAL_TAMPERING = "POTENTIAL_TAMPERING"
    UNKNOWN = "UNKNOWN"
    INVALID_INPUT = "INVALID_INPUT"
    PROCESSING_ERROR = "PROCESSING_ERROR"

class ForensicIndicatorResult(BaseModel):
    name: str
    anomaly_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)
    localized_hotspots: List[List[int]] = Field(default_factory=list) # [[ymin, xmin, ymax, xmax]]

class SuspiciousRegion(BaseModel):
    region_type: str # 'photo', 'date_field', 'mrz', 'security_background', 'text_line'
    bbox: List[int] # [ymin, xmin, ymax, xmax]
    anomaly_score: float
    primary_indicator: str
    explanation: str

class TamperingReport(BaseModel):
    module: str = "module3_tampering_detection"
    module_version: str = "1.0.0"
    status: TamperingStatusEnum
    anomaly_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    indicators: Dict[str, float] = Field(default_factory=dict)
    indicator_details: Dict[str, ForensicIndicatorResult] = Field(default_factory=dict)
    suspicious_regions: List[SuspiciousRegion] = Field(default_factory=list)
    tampering_types_detected: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    review_required: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
