"""Output Schemas and Officer Action Taxonomy for Module 5."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RecommendedOfficerActionEnum(str, Enum):
    CLEAR = "CLEAR"
    STANDARD_INSPECTION = "STANDARD_INSPECTION"
    SECONDARY_INSPECTION_RECOMMENDED = "SECONDARY_INSPECTION_RECOMMENDED"
    TECHNICAL_REVIEW_REQUIRED = "TECHNICAL_REVIEW_REQUIRED"
    RECAPTURE_REQUIRED = "RECAPTURE_REQUIRED"
    INVALID_INPUT = "INVALID_INPUT"
    PROCESSING_ERROR = "PROCESSING_ERROR"

class DimensionalRisks(BaseModel):
    document_syntactic_risk: float = Field(ge=0.0, le=1.0)
    physical_tampering_risk: float = Field(ge=0.0, le=1.0)
    biometric_identity_risk: float = Field(ge=0.0, le=1.0)
    compound_boost: float = Field(ge=0.0, le=1.0)

class ItemizedEvidence(BaseModel):
    positive_findings: List[str] = Field(default_factory=list)
    negative_findings: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)

class CompositeEvidenceReport(BaseModel):
    module: str = "module5_explainable_evidence"
    module_version: str = "1.0.0"
    recommended_action: RecommendedOfficerActionEnum
    risk_index: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)
    dimensional_risks: DimensionalRisks
    executive_summary: str
    itemized_evidence: ItemizedEvidence
    actionable_guidance: str
    review_required: bool = False
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
