import time
from typing import Dict, Any, Optional, Union
import numpy as np
from ..quality.portrait_quality_evaluator import PortraitQualityEvaluator
from ..liveness.pad_detector import PresentationAttackDetector
from ..matching.feature_extractor import FaceFeatureExtractor
from ..matching.cosine_matcher import CosineFaceMatcher
from ..schemas.output_schema import (
    BiometricVerificationReport,
    BiometricStatusEnum
)

class BiometricVerificationEngine:
    """End-to-end pipeline for 1:1 facial document vs live verification."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_evaluator = PortraitQualityEvaluator(config)
        self.liveness_detector = PresentationAttackDetector(config)
        self.feature_extractor = FaceFeatureExtractor(config)
        self.matcher = CosineFaceMatcher(config)

        self.match_thresh = config.get("thresholds", {}).get("match_threshold", 0.72)
        self.no_match_thresh = config.get("thresholds", {}).get("no_match_threshold", 0.48)

    def verify(self, doc_image: np.ndarray, live_image: np.ndarray) -> BiometricVerificationReport:
        t0 = time.perf_counter()

        # 1. Null / Format Gating
        if doc_image is None or doc_image.size == 0 or live_image is None or live_image.size == 0:
            return BiometricVerificationReport(
                status=BiometricStatusEnum.INVALID_INPUT,
                similarity_score=0.0,
                confidence=0.0,
                errors=["One or both input images are null, empty, or unreadable"],
                review_required=True
            )

        # 2. Quality Assessment on Document Portrait
        doc_quality, doc_face = self.quality_evaluator.evaluate(doc_image)
        live_quality, live_face = self.quality_evaluator.evaluate(live_image)

        warnings = []
        warnings.extend([f"[Doc] {w}" for w in doc_quality.warnings])
        warnings.extend([f"[Live] {w}" for w in live_quality.warnings])

        # 3. Check Face Presence
        if doc_face is None or live_face is None:
            missing = "document image" if doc_face is None else "live image"
            if doc_face is None and live_face is None:
                missing = "both document and live images"
            return BiometricVerificationReport(
                status=BiometricStatusEnum.NO_FACE_DETECTED,
                similarity_score=0.0,
                confidence=0.85,
                doc_portrait_quality=doc_quality,
                live_portrait_quality=live_quality,
                warnings=warnings,
                errors=[f"No face detected in {missing}"],
                review_required=True
            )

        # 4. Check Severe Quality Failures
        if not doc_quality.is_compliant or not live_quality.is_compliant:
            if doc_quality.sharpness < 15.0 or live_quality.sharpness < 15.0:
                return BiometricVerificationReport(
                    status=BiometricStatusEnum.POOR_QUALITY,
                    similarity_score=0.0,
                    confidence=0.88,
                    doc_portrait_quality=doc_quality,
                    live_portrait_quality=live_quality,
                    warnings=warnings,
                    errors=["Facial image sharpness is too low for reliable 1:1 biometric matching"],
                    review_required=True
                )

        # 5. Liveness / Presentation Attack Detection on Live Probe
        liveness_res = self.liveness_detector.assess_liveness(live_image, live_face)
        if not liveness_res.is_live:
            warnings.extend(liveness_res.warnings)
            return BiometricVerificationReport(
                status=BiometricStatusEnum.SPOOF_ATTEMPT_DETECTED,
                similarity_score=0.0,
                confidence=0.90,
                doc_portrait_quality=doc_quality,
                live_portrait_quality=live_quality,
                liveness_assessment=liveness_res,
                warnings=warnings,
                review_required=True
            )

        # 6. Feature Extraction & Embedding Generation
        doc_embedding = self.feature_extractor.extract(doc_face)
        live_embedding = self.feature_extractor.extract(live_face)

        # 7. Cosine Similarity Matching
        similarity_score, cosine_dist = self.matcher.match(doc_embedding, live_embedding)

        # 8. Status Determination
        if similarity_score >= self.match_thresh:
            status = BiometricStatusEnum.MATCH
            review_required = False
        elif similarity_score < self.no_match_thresh:
            status = BiometricStatusEnum.NO_MATCH
            review_required = True
        else:
            status = BiometricStatusEnum.REVIEW_REQUIRED
            review_required = True

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        return BiometricVerificationReport(
            status=status,
            similarity_score=similarity_score,
            confidence=0.94,
            doc_portrait_quality=doc_quality,
            live_portrait_quality=live_quality,
            liveness_assessment=liveness_res,
            cosine_distance=cosine_dist,
            operating_threshold=self.match_thresh,
            warnings=warnings,
            review_required=review_required,
            metadata={
                "processing_time_ms": round(elapsed_ms, 2)
            }
        )
