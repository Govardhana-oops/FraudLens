"""Test-Only Synthetic OCR Adapter (Explicitly Isolated from Production Screening)."""

import numpy as np
from typing import Optional, Dict, Any, List
from .base_engine import BaseOCREngine

class TestSyntheticOCRAdapter(BaseOCREngine):
    """
    TEST-ONLY synthetic token provider.
    STRICTLY FORBIDDEN in production screening paths.
    """
    IS_TEST_ONLY: bool = True

    def __init__(self, allow_test_mock: bool = False):
        self.allow_test_mock = allow_test_mock

    @property
    def name(self) -> str:
        return "test_synthetic_only"

    def is_available(self) -> bool:
        return self.allow_test_mock

    def recognize(self, image_np: np.ndarray, mrz_crop: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Throws security error if invoked without explicit test permission."""
        if not self.allow_test_mock:
            raise PermissionError(
                "SyntheticOCREngine contains hardcoded test identity tokens and is strictly forbidden in production screening."
            )

        # Isolated test tokens for unit testing harness
        lines = [
            "PASSPORT",
            "REPUBLIC OF INDIA",
            "Name: TEST HOLDER",
            "Passport No: T9999999",
            "Nationality: TEST",
            "Date of Birth: 01 JAN 2000",
            "Date of Expiry: 01 JAN 2030",
            "Sex: M",
            "P<INDTEST<<HOLDER<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            "T9999999<0IND0001014M3001018<<<<<<<<<<<<<<<2"
        ]

        return {
            "raw_text": "\n".join(lines),
            "lines": lines,
            "words": [{"text": l, "confidence": 0.99, "bbox": [0, 0, 100, 20]} for l in lines],
            "average_confidence": 0.99,
            "engine": self.name
        }
