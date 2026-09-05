"""Pydantic API Request and Response Models for Module 8."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = "HEALTHY"
    version: str = "1.0.0"
    service: str = "AI-DIDSS Verification Decision Support API"
    uptime_seconds: float
    modules_ready: List[str]

class SyncRequest(BaseModel):
    delta_records: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class AuditVerificationResponse(BaseModel):
    total_logs: int
    chain_intact: bool
    logs: List[Dict[str, Any]]
