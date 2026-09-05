"""Cross-Modal Anomaly Correlator."""

from typing import Dict, Any, Optional, List, Tuple

class AnomalyCorrelator:
    """Correlates anomalies across modules (e.g. M3 photo tampering with M4 face mismatch)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.boost_photo_bio = config.get("thresholds", {}).get("compound_boost_photo_bio", 0.20)
        self.boost_text_mrz = config.get("thresholds", {}).get("compound_boost_text_mrz", 0.15)

    def correlate(
        self,
        m1_report: Optional[Dict[str, Any]],
        m2_report: Optional[Dict[str, Any]],
        m3_report: Optional[Dict[str, Any]],
        m4_report: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[str]]:
        """Calculates compound risk boost and extracts correlated anomaly descriptions."""
        boost = 0.0
        correlations = []

        # 1. Correlate M3 Spliced Photo with M4 Biometric Face Mismatch
        m3_tampering = m3_report and m3_report.get("status") == "POTENTIAL_TAMPERING"
        m4_no_match = m4_report and m4_report.get("status") in ["NO_MATCH", "SPOOF_ATTEMPT_DETECTED"]

        if m3_tampering and m4_no_match:
            boost += self.boost_photo_bio
            correlations.append(
                "CRITICAL CORRELATION: Photo substrate tampering in Module 3 coincides with Biometric Facial Mismatch in Module 4 (High Imposter / Photo-Substitution Probability)."
            )

        # 2. Correlate M3 Font/Text Anomaly with M2 MRZ Checksum / Syntax Failure
        m3_text_tamper = m3_report and any("font" in t or "compression" in t for t in m3_report.get("tampering_types_detected", []))
        m2_syntax_fail = m2_report and m2_report.get("overall_status") in ["INVALID", "REVIEW_REQUIRED"]

        if m3_text_tamper and m2_syntax_fail:
            boost += self.boost_text_mrz
            correlations.append(
                "HIGH CORRELATION: Localized text alteration artifacts in Module 3 coincide with Document Validation syntax / checksum failures in Module 2."
            )

        # 3. Presentation Attack / Spoofing on Live Capture
        if m4_report and m4_report.get("status") == "SPOOF_ATTEMPT_DETECTED":
            boost += 0.20
            correlations.append(
                "SECURITY ALERT: Presentation attack signature (screen moiré or paper mask) detected during live biometric capture in Module 4."
            )

        return min(0.35, boost), correlations
