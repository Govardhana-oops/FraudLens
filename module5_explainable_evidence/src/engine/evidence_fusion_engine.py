"""Explainable Multi-Source Evidence Fusion Engine."""

import time
from typing import Dict, Any, Optional, List
from ..aggregators.risk_index_calculator import RiskIndexCalculator
from ..aggregators.anomaly_correlator import AnomalyCorrelator
from ..explainer.narrative_generator import NarrativeGenerator
from ..schemas.output_schema import (
    CompositeEvidenceReport,
    RecommendedOfficerActionEnum
)

class EvidenceFusionEngine:
    """Combines optical, syntactic, forensic, and biometric streams into an explainable decision support report."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.risk_calculator = RiskIndexCalculator(config)
        self.correlator = AnomalyCorrelator(config)
        self.narrative_generator = NarrativeGenerator(config)

    def assess(
        self,
        module1_report: Optional[Dict[str, Any]] = None,
        module2_report: Optional[Dict[str, Any]] = None,
        module3_report: Optional[Dict[str, Any]] = None,
        module4_report: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CompositeEvidenceReport:
        t0 = time.perf_counter()

        modules_fused = []
        if module1_report: modules_fused.append("module1_ocr")
        if module2_report: modules_fused.append("module2_document_validation")
        if module3_report: modules_fused.append("module3_tampering_detection")
        if module4_report: modules_fused.append("module4_face_verification")

        # 1. Cross-modal anomaly correlation
        boost, correlations = self.correlator.correlate(
            module1_report, module2_report, module3_report, module4_report
        )

        # 2. Compute dimensional and composite risk scores
        dim_risks, risk_index = self.risk_calculator.calculate_risks(
            module2_report, module3_report, module4_report, compound_boost=boost
        )

        # 3. Generate explainable narrative and recommended action
        rec_action, exec_summary, itemized, guidance = self.narrative_generator.generate(
            risk_index, module1_report, module2_report, module3_report, module4_report, correlations
        )

        review_required = (rec_action != RecommendedOfficerActionEnum.CLEAR)

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        return CompositeEvidenceReport(
            recommended_action=rec_action,
            risk_index=risk_index,
            confidence_score=0.95,
            dimensional_risks=dim_risks,
            executive_summary=exec_summary,
            itemized_evidence=itemized,
            actionable_guidance=guidance,
            review_required=review_required,
            metadata={
                "modules_fused": modules_fused,
                "correlations_count": len(correlations),
                "processing_time_ms": round(elapsed_ms, 2)
            }
        )
