"""Explainable Multi-Modal Forensic Fusion Engine."""

import time
from typing import Dict, Any, Optional, List
import numpy as np
from ..forensics.ela_detector import ELADetector
from ..forensics.noise_inconsistency_detector import NoiseInconsistencyDetector
from ..forensics.edge_gradient_detector import EdgeGradientDetector
from ..forensics.font_texture_detector import FontTextureDetector
from ..forensics.frequency_fft_detector import FrequencyFFTDetector
from ..schemas.output_schema import (
    TamperingReport,
    TamperingStatusEnum,
    ForensicIndicatorResult,
    SuspiciousRegion
)

class ForensicFusionEngine:
    """Combines multi-modal forensic indicators into a calibrated decision-support tampering report."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get("weights", {
            "ela": 0.25,
            "noise_inconsistency": 0.25,
            "edge_gradient": 0.20,
            "frequency_spectral": 0.15,
            "font_texture": 0.15
        })
        self.thresholds = config.get("thresholds", {
            "potential_tampering_score": 0.65,
            "review_required_score": 0.35
        })

        # Initialize detector suite
        self.detectors = {
            "error_level_analysis": ELADetector(config),
            "noise_inconsistency": NoiseInconsistencyDetector(config),
            "edge_gradient_discontinuity": EdgeGradientDetector(config),
            "font_texture_inconsistency": FontTextureDetector(config),
            "frequency_fft_spectral": FrequencyFFTDetector(config)
        }

    def analyze(self, image: np.ndarray, regions: Optional[Dict[str, Any]] = None) -> TamperingReport:
        t0 = time.perf_counter()

        # 1. Quality & Format Gating
        if image is None or not isinstance(image, np.ndarray) or image.size == 0:
            return TamperingReport(
                status=TamperingStatusEnum.INVALID_INPUT,
                anomaly_score=0.0,
                confidence=0.0,
                errors=["Input image buffer is null, empty, or not a numpy ndarray"],
                review_required=True
            )

        if len(image.shape) < 2 or (len(image.shape) == 3 and image.shape[2] not in [1, 3, 4]):
            return TamperingReport(
                status=TamperingStatusEnum.INVALID_INPUT,
                anomaly_score=0.0,
                confidence=0.0,
                errors=[f"Unsupported image dimensions: shape={image.shape}"],
                review_required=True
            )

        h, w = image.shape[:2]
        min_dim = self.config.get("quality_limits", {}).get("min_width", 150)
        if h < min_dim or w < min_dim:
            return TamperingReport(
                status=TamperingStatusEnum.UNKNOWN,
                anomaly_score=0.0,
                confidence=0.30,
                warnings=[f"Image resolution ({w}x{h}) is too low for reliable forensic spectral and noise analysis"],
                review_required=True,
                metadata={"width": w, "height": h}
            )

        # 2. Run all forensic detectors
        indicator_results: Dict[str, ForensicIndicatorResult] = {}
        indicator_scores: Dict[str, float] = {}
        suspicious_regions: List[SuspiciousRegion] = []
        tampering_types_detected: List[str] = []
        warnings: List[str] = []

        for name, detector in self.detectors.items():
            res = detector.detect(image, regions)
            indicator_results[name] = res
            indicator_scores[name] = res.anomaly_score

            # Collect suspicious hotspots
            for box in res.localized_hotspots:
                suspicious_regions.append(SuspiciousRegion(
                    region_type="anomaly_hotspot",
                    bbox=box,
                    anomaly_score=res.anomaly_score,
                    primary_indicator=name,
                    explanation=f"Localized anomaly detected by {name}"
                ))

            # Tag specific tampering types if threshold exceeded
            if name == "error_level_analysis" and res.anomaly_score >= 0.50:
                tampering_types_detected.append("compression_splicing_inconsistency")
            elif name == "noise_inconsistency" and res.anomaly_score >= 0.50:
                tampering_types_detected.append("noise_residual_variance_mismatch")
            elif name == "edge_gradient_discontinuity" and res.anomaly_score >= 0.50:
                tampering_types_detected.append("copy_paste_edge_clipping")
            elif name == "frequency_fft_spectral" and res.anomaly_score >= 0.50:
                tampering_types_detected.append("screen_capture_spectral_lattice")
            elif name == "font_texture_inconsistency" and res.anomaly_score >= 0.50:
                tampering_types_detected.append("font_sharpness_discontinuity")

        # 3. Compute Calibrated Weighted Fusion Anomaly Score
        weight_sum = (
            self.weights.get("ela", 0.25) +
            self.weights.get("noise_inconsistency", 0.25) +
            self.weights.get("edge_gradient", 0.20) +
            self.weights.get("font_texture", 0.15) +
            self.weights.get("frequency_spectral", 0.15)
        )

        weighted_score = (
            (indicator_scores["error_level_analysis"] * self.weights.get("ela", 0.25)) +
            (indicator_scores["noise_inconsistency"] * self.weights.get("noise_inconsistency", 0.25)) +
            (indicator_scores["edge_gradient_discontinuity"] * self.weights.get("edge_gradient", 0.20)) +
            (indicator_scores["font_texture_inconsistency"] * self.weights.get("font_texture", 0.15)) +
            (indicator_scores["frequency_fft_spectral"] * self.weights.get("frequency_spectral", 0.15))
        ) / weight_sum

        # Max indicator boost: If an individual detector is extremely high (>= 0.85), boost the fused score
        max_ind = max(indicator_scores.values())
        if max_ind >= 0.85:
            fused_anomaly_score = max(weighted_score, max_ind * 0.80)
        else:
            fused_anomaly_score = weighted_score

        fused_anomaly_score = float(np.clip(fused_anomaly_score, 0.0, 1.0))

        # 4. Status Determination
        pt_thresh = self.thresholds.get("potential_tampering_score", 0.65)
        rr_thresh = self.thresholds.get("review_required_score", 0.35)

        if fused_anomaly_score >= pt_thresh:
            status = TamperingStatusEnum.POTENTIAL_TAMPERING
            review_required = True
        elif fused_anomaly_score >= rr_thresh or len(suspicious_regions) > 0:
            status = TamperingStatusEnum.REVIEW_REQUIRED
            review_required = True
        else:
            status = TamperingStatusEnum.NO_TAMPERING_EVIDENCE
            review_required = False

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        return TamperingReport(
            status=status,
            anomaly_score=round(fused_anomaly_score, 4),
            confidence=0.92,
            indicators=indicator_scores,
            indicator_details=indicator_results,
            suspicious_regions=suspicious_regions[:15],
            tampering_types_detected=tampering_types_detected,
            warnings=warnings,
            review_required=review_required,
            metadata={
                "image_width": w,
                "image_height": h,
                "processing_time_ms": round(elapsed_ms, 2)
            }
        )
