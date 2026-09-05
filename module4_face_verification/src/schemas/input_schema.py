"""Input Schemas for Module 4 Face Verification."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class BiometricVerificationInput(BaseModel):
    document_image_path: Optional[str] = None
    live_image_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
