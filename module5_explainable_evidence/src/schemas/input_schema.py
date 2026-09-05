"""Input Schemas for Module 5 Evidence Fusion."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class MultiModuleInputDossier(BaseModel):
    module1_report: Optional[Dict[str, Any]] = None
    module2_report: Optional[Dict[str, Any]] = None
    module3_report: Optional[Dict[str, Any]] = None
    module4_report: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
