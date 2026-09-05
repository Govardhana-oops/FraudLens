"""Input Schema for Module 3 Tampering Detection."""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    ymin: int
    xmin: int
    ymax: int
    xmax: int
    label: Optional[str] = None

class TamperingInputPayload(BaseModel):
    image_path: Optional[str] = None
    regions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
