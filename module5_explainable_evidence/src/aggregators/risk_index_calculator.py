"""Risk Index Calculator for multi-dimensional evidence scoring."""

from typing import Dict, Any, Tuple, Optional
import numpy as np
from ..schemas.output_schema import DimensionalRisks

class RiskIndexCalculator:
    """Calculates calibrated dimensional and overall composite risk indices."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get("weights", {
            "document_syntactic": 0.35,
            "physical_tampering": 0.35,
            "biometric_identity": 0.30
        })

    def calculate_risks(
        self,
        m2_report: Optional[Dict[str, Any]] = None,
        m3_report: Optional[Dict[str, Any]] = None,
        m4_report: Optional[Dict[str, Any]] = None,
        compound_boost: float = 0.0
    ) -> Tuple[DimensionalRisks, float]:
        """Computes individual dimensional risks and composite risk index in [0.0, 1.0]."""

        # 1. Document Syntactic Risk (M2)
        if m2_report is not None:
            m2_status = m2_report.get("overall_status", "UNKNOWN")
            m2_score = float(m2_report.get("validation_score", 0.5))
            if m2_status == "INVALID":
                r_doc = 1.0
            elif m2_status == "EXPIRED":
                r_doc = 0.45
            elif m2_status == "REVIEW_REQUIRED":
                r_doc = 0.50
            elif m2_status == "UNKNOWN":
                r_doc = 0.60
            elif m2_status == "UNSUPPORTED_DOCUMENT":
                r_doc = 0.55
            else: # VALID
                r_doc = max(0.0, 1.0 - m2_score)
        else:
            r_doc = 0.50 # Unknown/Missing M2

        # 2. Physical Tampering Risk (M3)
        if m3_report is not None:
            m3_status = m3_report.get("status", "NO_TAMPERING_EVIDENCE")
            m3_anomaly = float(m3_report.get("anomaly_score", 0.0))
            if m3_status == "POTENTIAL_TAMPERING":
                r_tamp = max(0.70, m3_anomaly)
            elif m3_status == "REVIEW_REQUIRED":
                r_tamp = max(0.40, m3_anomaly)
            else:
                r_tamp = m3_anomaly
        else:
            r_tamp = 0.30

        # 3. Biometric Identity Risk (M4)
        if m4_report is not None:
            m4_status = m4_report.get("status", "MATCH")
            m4_sim = float(m4_report.get("similarity_score", 0.85))
            if m4_status == "SPOOF_ATTEMPT_DETECTED":
                r_bio = 1.0
            elif m4_status == "NO_MATCH":
                r_bio = max(0.75, 1.0 - m4_sim)
            elif m4_status == "POOR_QUALITY":
                r_bio = 0.55
            elif m4_status == "NO_FACE_DETECTED":
                r_bio = 0.60
            elif m4_status == "REVIEW_REQUIRED":
                r_bio = 0.45
            else: # MATCH
                r_bio = max(0.0, 1.0 - m4_sim)
        else:
            r_bio = 0.25

        # 4. Composite Risk Index
        w_doc = self.weights.get("document_syntactic", 0.35)
        w_tamp = self.weights.get("physical_tampering", 0.35)
        w_bio = self.weights.get("biometric_identity", 0.30)
        total_w = w_doc + w_tamp + w_bio

        composite_risk = (
            (r_doc * w_doc) +
            (r_tamp * w_tamp) +
            (r_bio * w_bio) +
            compound_boost
        ) / total_w

        composite_risk = float(np.clip(composite_risk, 0.0, 1.0))

        dim_risks = DimensionalRisks(
            document_syntactic_risk=round(r_doc, 4),
            physical_tampering_risk=round(r_tamp, 4),
            biometric_identity_risk=round(r_bio, 4),
            compound_boost=round(compound_boost, 4)
        )

        return dim_risks, round(composite_risk, 4)
