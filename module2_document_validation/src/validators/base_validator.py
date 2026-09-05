"""Base Validator Class for Module 2 Document Validation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult

class BaseValidator(ABC):
    """Abstract base class for all modular document validators."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def validate(self, payload: Module1InputPayload) -> List[ValidationCheckResult]:
        """Executes validation rules on input payload and returns list of check results."""
        pass
