"""Output Schemas and Status Taxonomy for Module 4 Face Verification."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BiometricStatusEnum(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    POOR_QUALITY = "POOR_QUALITY"
    NO_FACE_DETECTED = "NO_FACE_DETECTED"
    SPOOF_ATTEMPT_DETECTED = "SPOOF_ATTEMPT_DETECTED"
    UNKNOWN = "UNKNOWN"
    INVALID_INPUT = "INVALID_INPUT"
    PROCESSING_ERROR = "PROCESSING_ERROR"

class PortraitQualityAssessment(BaseModel):
    is_compliant: bool
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    sharpness: float
    illumination_uniformity: float
    contrast_score: float
    glare_percentage: float
    face_bbox: Optional[List[int]] = None # [ymin, xmin, ymax, xmax]
    warnings: List[str] = Field(default_factory=list)

class LivenessAssessment(BaseModel):
    is_live: bool
    liveness_score: float = Field(ge=0.0, le=1.0)
    attack_type_detected: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)

class BiometricVerificationReport(BaseModel):
    module: str = "module4_face_verification"
    module_version: str = "1.0.0"
    status: BiometricStatusEnum
    similarity_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    doc_portrait_quality: Optional[PortraitQualityAssessment] = None
    live_portrait_quality: Optional[PortraitQualityAssessment] = None
    liveness_assessment: Optional[LivenessAssessment] = None
    cosine_distance: Optional[float] = None
    operating_threshold: float = 0.72
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    review_required: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
