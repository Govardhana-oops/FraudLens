from typing import Dict, Any, Optional, List, Tuple
from ..schemas.output_schema import (
    ItemizedEvidence,
    RecommendedOfficerActionEnum
)

class NarrativeGenerator:
    """Generates structured, explainable natural language findings and officer recommendations."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(
        self,
        risk_index: float,
        m1_report: Optional[Dict[str, Any]],
        m2_report: Optional[Dict[str, Any]],
        m3_report: Optional[Dict[str, Any]],
        m4_report: Optional[Dict[str, Any]],
        correlations: List[str]
    ) -> Tuple[RecommendedOfficerActionEnum, str, ItemizedEvidence, str]:
        """Synthesizes all findings into a deterministic decision recommendation and narrative."""

        positive = []
        negative = []
        uncertainties = []

        # 1. Inspect Module 1 (OCR)
        if m1_report:
            doc_type = m1_report.get("document_type", {}).get("value", "document")
            doc_conf = float(m1_report.get("document_type", {}).get("confidence", 1.0))
            if doc_conf >= 0.80:
                positive.append(f"Document optical layout recognized as {doc_type.upper()} with {doc_conf*100:.1f}% confidence.")
            else:
                uncertainties.append(f"Document type classification uncertainty ({doc_type} at {doc_conf*100:.1f}% confidence).")

        # 2. Inspect Module 2 (Validation)
        if m2_report:
            m2_status = m2_report.get("overall_status", "UNKNOWN")
            if m2_status == "VALID":
                positive.append("Document structure, calendar validity, chronology, and ICAO MRZ checksums fully verified.")
            elif m2_status == "INVALID":
                negative.append("Substantive document validation failure (e.g. invalid calendar date, impossible chronology, or MRZ checksum mismatch).")
                for err in m2_report.get("errors", []):
                    negative.append(f"Validation Failure: {err}")
            elif m2_status == "EXPIRED":
                negative.append("Document validity period has expired.")
            elif m2_status == "REVIEW_REQUIRED":
                uncertainties.append("Document validation requires manual review (e.g. cross-field visual/MRZ discrepancy or missing optional field).")

        # 3. Inspect Module 3 (Tampering Detection)
        if m3_report:
            m3_status = m3_report.get("status", "NO_TAMPERING_EVIDENCE")
            m3_score = float(m3_report.get("anomaly_score", 0.0))
            if m3_status == "NO_TAMPERING_EVIDENCE":
                positive.append(f"No digital tampering or physical alteration evidence found (anomaly score: {m3_score:.2f}).")
            elif m3_status == "POTENTIAL_TAMPERING":
                negative.append(f"Potential digital manipulation detected (anomaly score: {m3_score:.2f}).")
                for t in m3_report.get("tampering_types_detected", []):
                    negative.append(f"Tampering Indicator: {t}")
            elif m3_status == "REVIEW_REQUIRED":
                uncertainties.append(f"Minor forensic anomaly detected ({m3_score:.2f}) requiring verification.")

        # 4. Inspect Module 4 (Biometric Verification)
        if m4_report:
            m4_status = m4_report.get("status", "MATCH")
            m4_sim = float(m4_report.get("similarity_score", 0.0))
            if m4_status == "MATCH":
                positive.append(f"1:1 Facial biometric match verified against live capture probe (similarity: {m4_sim:.2f}).")
            elif m4_status == "NO_MATCH":
                negative.append(f"Facial biometric comparison failed to match bearer portrait (similarity: {m4_sim:.2f} < threshold).")
            elif m4_status == "SPOOF_ATTEMPT_DETECTED":
                negative.append("Live biometric capture rejected: Presentation attack signature (screen moiré / paper replay) detected.")
            elif m4_status in ["POOR_QUALITY", "NO_FACE_DETECTED"]:
                uncertainties.append(f"Biometric image quality insufficient for matching: {m4_status}.")

        # Add cross-modal correlations
        for c in correlations:
            negative.append(c)

        # 5. Determine Recommended Officer Action
        if (m4_report and m4_report.get("status") in ["NO_FACE_DETECTED", "POOR_QUALITY"]) or (m1_report and m1_report.get("status") == "INVALID_INPUT"):
            recommended_action = RecommendedOfficerActionEnum.RECAPTURE_REQUIRED
            guidance = "Request passenger to re-position document or re-take live camera capture under uniform lighting."
            exec_summary = "Image quality or face visibility insufficient for complete multi-modal verification."
        elif risk_index >= 0.65 or len(correlations) > 0:
            recommended_action = RecommendedOfficerActionEnum.SECONDARY_INSPECTION_RECOMMENDED
            guidance = "Escalate passenger to Secondary Inspection Station for physical tactile inspection and supervisor verification."
            exec_summary = f"High cumulative risk index ({risk_index:.2f}) across forensic, syntactic, or biometric dimensions."
        elif risk_index >= 0.30 or len(negative) > 0 or len(uncertainties) > 0:
            recommended_action = RecommendedOfficerActionEnum.TECHNICAL_REVIEW_REQUIRED
            guidance = "Inspect flagged fields on officer console before proceeding."
            exec_summary = f"Moderate risk index ({risk_index:.2f}) with minor validation warnings or optical discrepancies."
        elif m2_report and m2_report.get("overall_status") == "EXPIRED":
            recommended_action = RecommendedOfficerActionEnum.STANDARD_INSPECTION
            guidance = "Verify passenger travel authorization regarding document expiration date."
            exec_summary = "Document structurally authentic but validity date is expired."
        else:
            recommended_action = RecommendedOfficerActionEnum.CLEAR
            guidance = "Standard clearance approved. No anomalies or discrepancies detected."
            exec_summary = "All document validation checks, forensic tampering scans, and biometric match verifications passed successfully."

        itemized = ItemizedEvidence(
            positive_findings=positive,
            negative_findings=negative,
            uncertainties=uncertainties
        )

        return recommended_action, exec_summary, itemized, guidance
