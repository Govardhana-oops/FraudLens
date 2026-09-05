"""Public Interface for Module 5 Explainable Evidence & Anomaly Assessment."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from .engine.evidence_fusion_engine import EvidenceFusionEngine
from .schemas.output_schema import (
    CompositeEvidenceReport,
    RecommendedOfficerActionEnum,
    DimensionalRisks,
    ItemizedEvidence
)

class ExplainableEvidenceAssessor:
    """Public high-level singleton API for Module 5 Evidence Fusion & Reasoning."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "configs" / "evidence_config.yaml")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        self.engine = EvidenceFusionEngine(self.config)

    def assess(
        self,
        module1_report: Optional[Dict[str, Any]] = None,
        module2_report: Optional[Dict[str, Any]] = None,
        module3_report: Optional[Dict[str, Any]] = None,
        module4_report: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Synthesizes reports from upstream modules into an explainable decision dossier."""
        try:
            report = self.engine.assess(
                module1_report=module1_report,
                module2_report=module2_report,
                module3_report=module3_report,
                module4_report=module4_report,
                metadata=metadata
            )
            return report.model_dump()
        except Exception as e:
            return CompositeEvidenceReport(
                recommended_action=RecommendedOfficerActionEnum.PROCESSING_ERROR,
                risk_index=1.0,
                confidence_score=0.0,
                dimensional_risks=DimensionalRisks(
                    document_syntactic_risk=1.0,
                    physical_tampering_risk=1.0,
                    biometric_identity_risk=1.0,
                    compound_boost=0.0
                ),
                executive_summary=f"Internal processing exception during evidence assessment: {str(e)}",
                itemized_evidence=ItemizedEvidence(
                    positive_findings=[],
                    negative_findings=[f"Exception: {str(e)}"],
                    uncertainties=[]
                ),
                actionable_guidance="Refer document to supervisor due to system processing error.",
                review_required=True,
                errors=[str(e)]
            ).model_dump()

# Global singleton
evidence_fusion_engine = ExplainableEvidenceAssessor()
