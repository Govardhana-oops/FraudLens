"""Schemas for Unified Screening Dossier in Module 7."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ModuleExecutionTelemetry(BaseModel):
    module_name: str
    status: str
    latency_ms: float
    details: Dict[str, Any] = Field(default_factory=dict)

class UnifiedScreeningDossier(BaseModel):
    screening_id: str
    timestamp: str
    document_type: str
    recommended_action: str
    risk_index: float
    confidence_score: float
    executive_summary: str
    actionable_guidance: str
    is_flagged_on_watchlist: bool = False
    watchlist_details: Optional[Dict[str, Any]] = None
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    mrz: Optional[Dict[str, Any]] = None
    visual_mrz_conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    itemized_evidence: Dict[str, Any] = Field(default_factory=dict)
    dimensional_risks: Dict[str, float] = Field(default_factory=dict)
    modules_telemetry: Dict[str, ModuleExecutionTelemetry] = Field(default_factory=dict)
    audit_log: Dict[str, Any] = Field(default_factory=dict)
    total_latency_ms: float
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
