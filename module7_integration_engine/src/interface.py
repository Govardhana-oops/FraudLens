import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
import yaml
import numpy as np
from PIL import Image

# Dynamically ensure all submodule roots and project root are in sys.path
_proto_root = Path(__file__).resolve().parent.parent.parent
if str(_proto_root) not in sys.path:
    sys.path.insert(0, str(_proto_root))

for m_dir in [
    "module1_ocr",
    "module2_document_validation",
    "module3_tampering_detection",
    "module4_face_verification",
    "module5_explainable_evidence",
    "module6_database_sync",
    "module7_integration_engine"
]:
    p = str(_proto_root / m_dir)
    if p not in sys.path:
        sys.path.insert(0, p)

from .orchestrator.pipeline_orchestrator import PipelineOrchestrator
from .schemas.screening_dossier import UnifiedScreeningDossier

class ScreeningOrchestratorService:
    """Public high-level singleton API for end-to-end multi-module border screening."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "configs" / "integration_config.yaml")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        self.orchestrator = PipelineOrchestrator(self.config)

    def process_screening(
        self,
        document_image: Union[str, np.ndarray, Image.Image, bytes],
        live_face_image: Optional[Union[str, np.ndarray, Image.Image, bytes]] = None,
        officer_id: Optional[str] = None,
        checkpoint_id: Optional[str] = None,
        extracted_fields_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs the complete multi-modal screening pipeline and returns a unified dossier."""
        dossier = self.orchestrator.execute_screening(
            document_image=document_image,
            live_face_image=live_face_image,
            officer_id=officer_id,
            checkpoint_id=checkpoint_id,
            extracted_fields_override=extracted_fields_override
        )
        return dossier.model_dump()

# Global singleton
screening_orchestrator = ScreeningOrchestratorService()
