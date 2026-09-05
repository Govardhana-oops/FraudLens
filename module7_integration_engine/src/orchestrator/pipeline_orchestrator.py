import sys
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from pathlib import Path
import numpy as np
from PIL import Image

# Dynamically add all module roots to sys.path
_proto_root = Path(__file__).resolve().parent.parent.parent.parent
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

# Import upstream modules
from module1_ocr.src.interface import DocumentOCR
from module2_document_validation.src.interface import document_validator
from module3_tampering_detection.src.interface import tampering_detector
from module4_face_verification.src.interface import face_verifier
from module5_explainable_evidence.src.interface import evidence_fusion_engine
from module6_database_sync.src.interface import database_sync_service

from ..schemas.screening_dossier import (
    UnifiedScreeningDossier,
    ModuleExecutionTelemetry
)

class PipelineOrchestrator:
    """Executes the complete multi-modal screening pipeline across all modules."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.m1_ocr = DocumentOCR()

    def execute_screening(
        self,
        document_image: Union[str, np.ndarray, Image.Image, bytes],
        live_face_image: Optional[Union[str, np.ndarray, Image.Image, bytes]] = None,
        officer_id: Optional[str] = None,
        checkpoint_id: Optional[str] = None,
        extracted_fields_override: Optional[Dict[str, Any]] = None
    ) -> UnifiedScreeningDossier:
        start_time = time.perf_counter()
        screening_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        telemetry: Dict[str, ModuleExecutionTelemetry] = {}
        errors = []
        warnings = []

        off_id = officer_id or self.config.get("defaults", {}).get("default_officer_id", "OFFICER-DEFAULT")
        cp_id = checkpoint_id or self.config.get("defaults", {}).get("default_checkpoint_id", "AIRPORT-GATE-01")

        # ---------------------------------------------------------
        # Step 1: Module 1 OCR & Document Understanding
        # ---------------------------------------------------------
        t0 = time.perf_counter()
        m1_report = None
        doc_type = "unknown_document"
        try:
            if extracted_fields_override:
                m1_report = extracted_fields_override
                doc_type = m1_report.get("document_type", {}).get("value", "unknown_document")
                m1_status = m1_report.get("status", "SUCCESS")
            else:
                # Real Module 1 OCR processing directly on uploaded image
                m1_report = self.m1_ocr.process(document_image)
                doc_type = m1_report.get("document_type", {}).get("value", "unknown_document")
                m1_status = m1_report.get("status", "SUCCESS")

            t1 = time.perf_counter()
            telemetry["module1_ocr"] = ModuleExecutionTelemetry(
                module_name="module1_ocr",
                status=m1_status,
                latency_ms=round((t1 - t0) * 1000.0, 2),
                details={"doc_type": doc_type}
            )
        except Exception as e:
            errors.append(f"Module 1 OCR Error: {str(e)}")
            m1_report = {
                "module": "module1_ocr",
                "status": "ERROR",
                "document_type": {"value": "unknown_document", "confidence": 0.0},
                "fields": {},
                "mrz": None,
                "consistency": {"status": "NOT_APPLICABLE", "conflicts": []},
                "review_required": True,
                "warnings": [str(e)]
            }
            telemetry["module1_ocr"] = ModuleExecutionTelemetry(
                module_name="module1_ocr",
                status="ERROR",
                latency_ms=0.0,
                details={"error": str(e)}
            )

        # ---------------------------------------------------------
        # Step 2: Module 2 Rule, Calendar & Checksum Validation
        # ---------------------------------------------------------
        t0 = time.perf_counter()
        m2_report = None
        try:
            m2_report = document_validator.validate(m1_report)
            t1 = time.perf_counter()
            telemetry["module2_document_validation"] = ModuleExecutionTelemetry(
                module_name="module2_document_validation",
                status=m2_report.get("overall_status", "UNKNOWN"),
                latency_ms=round((t1 - t0) * 1000.0, 2),
                details={"validation_score": m2_report.get("validation_score", 0.0)}
            )
        except Exception as e:
            errors.append(f"Module 2 Validation Error: {str(e)}")
            telemetry["module2_document_validation"] = ModuleExecutionTelemetry(
                module_name="module2_document_validation",
                status="ERROR",
                latency_ms=0.0,
                details={"error": str(e)}
            )

        # ---------------------------------------------------------
        # Step 3: Module 3 Physical & Frequency Tampering Forensics
        # ---------------------------------------------------------
        t0 = time.perf_counter()
        m3_report = None
        try:
            # Convert document_image to numpy if necessary
            doc_np = None
            if isinstance(document_image, (str, Path)):
                import cv2
                doc_np = cv2.imread(str(document_image))
            elif isinstance(document_image, Image.Image):
                doc_np = np.array(document_image)
            elif isinstance(document_image, np.ndarray):
                doc_np = document_image
            elif isinstance(document_image, bytes):
                import cv2
                nparr = np.frombuffer(document_image, np.uint8)
                doc_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if doc_np is not None:
                m3_report = tampering_detector.analyze(doc_np)
                t1 = time.perf_counter()
                telemetry["module3_tampering_detection"] = ModuleExecutionTelemetry(
                    module_name="module3_tampering_detection",
                    status="ANOMALY_DETECTED" if m3_report.get("is_tampered") else "CLEAN",
                    latency_ms=round((t1 - t0) * 1000.0, 2),
                    details={"composite_score": m3_report.get("composite_tampering_score", 0.0)}
                )
            else:
                telemetry["module3_tampering_detection"] = ModuleExecutionTelemetry(
                    module_name="module3_tampering_detection",
                    status="SKIPPED",
                    latency_ms=0.0,
                    details={"reason": "Unable to decode document image for forensics"}
                )
        except Exception as e:
            errors.append(f"Module 3 Forensics Error: {str(e)}")
            telemetry["module3_tampering_detection"] = ModuleExecutionTelemetry(
                module_name="module3_tampering_detection",
                status="ERROR",
                latency_ms=0.0,
                details={"error": str(e)}
            )

        # ---------------------------------------------------------
        # Step 4: Module 4 Biometric 1:1 Face Verification & PAD
        # ---------------------------------------------------------
        t0 = time.perf_counter()
        m4_report = None
        try:
            if live_face_image is not None and doc_np is not None:
                # Convert live probe
                live_np = None
                if isinstance(live_face_image, (str, Path)):
                    import cv2
                    live_np = cv2.imread(str(live_face_image))
                elif isinstance(live_face_image, Image.Image):
                    live_np = np.array(live_face_image)
                elif isinstance(live_face_image, np.ndarray):
                    live_np = live_face_image
                elif isinstance(live_face_image, bytes):
                    import cv2
                    nparr = np.frombuffer(live_face_image, np.uint8)
                    live_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if live_np is not None:
                    m4_report = face_verifier.verify(doc_np, live_np)
                    t1 = time.perf_counter()
                    telemetry["module4_face_verification"] = ModuleExecutionTelemetry(
                        module_name="module4_face_verification",
                        status="MATCH" if m4_report.get("is_match") else "NO_MATCH",
                        latency_ms=round((t1 - t0) * 1000.0, 2),
                        details={"similarity": m4_report.get("similarity_score", 0.0)}
                    )
            else:
                telemetry["module4_face_verification"] = ModuleExecutionTelemetry(
                    module_name="module4_face_verification",
                    status="SKIPPED",
                    latency_ms=0.0,
                    details={"reason": "Live probe image not provided"}
                )
        except Exception as e:
            errors.append(f"Module 4 Biometrics Error: {str(e)}")
            telemetry["module4_face_verification"] = ModuleExecutionTelemetry(
                module_name="module4_face_verification",
                status="ERROR",
                latency_ms=0.0,
                details={"error": str(e)}
            )

        # ---------------------------------------------------------
        # Step 5: Module 6 Offline Watchlist & Revocation Lookup
        # ---------------------------------------------------------
        t0 = time.perf_counter()
        doc_num = None
        country_code = None
        if m1_report and "fields" in m1_report:
            fields = m1_report["fields"]
            doc_num = (
                fields.get("passport_number", {}).get("value") or
                fields.get("id_number", {}).get("value") or
                fields.get("license_number", {}).get("value") or
                fields.get("visa_number", {}).get("value") or
                fields.get("permit_number", {}).get("value") or
                fields.get("document_number", {}).get("value")
            )
            country_code = (
                fields.get("issuing_country", {}).get("value") or
                fields.get("nationality", {}).get("value")
            )

        # Fallback to MRZ parsed document number if visual field is missing
        if not doc_num and m1_report and m1_report.get("mrz") and m1_report["mrz"].get("lines"):
            mrz_lines = m1_report["mrz"]["lines"]
            if len(mrz_lines) >= 2:
                # TD3 line 2 chars 0:9
                l2 = mrz_lines[1]
                if len(l2) >= 9:
                    doc_num = l2[0:9].replace("<", "")

        watchlist_res = database_sync_service.lookup_watchlist(doc_num or "", country_code)
        t1 = time.perf_counter()
        telemetry["module6_database_sync"] = ModuleExecutionTelemetry(
            module_name="module6_database_sync",
            status="FLAGGED" if watchlist_res.get("is_flagged") else "CLEAN",
            latency_ms=round((t1 - t0) * 1000.0, 2),
            details={"is_flagged": watchlist_res.get("is_flagged", False)}
        )

        if watchlist_res.get("is_flagged"):
            warnings.append(f"WATCHLIST ALERT: Document {doc_num} is listed in SLTD revocation registry.")

        # ---------------------------------------------------------
        # Step 6: Module 5 Explainable Evidence Fusion & Reasoning
        # ---------------------------------------------------------
        t0 = time.perf_counter()
        m5_report = evidence_fusion_engine.assess(
            module1_report=m1_report,
            module2_report=m2_report,
            module3_report=m3_report,
            module4_report=m4_report
        )
        t1 = time.perf_counter()
        telemetry["module5_explainable_evidence"] = ModuleExecutionTelemetry(
            module_name="module5_explainable_evidence",
            status=m5_report.get("recommended_action", "UNKNOWN"),
            latency_ms=round((t1 - t0) * 1000.0, 2),
            details={"risk_index": m5_report.get("risk_index", 0.0)}
        )

        rec_action = m5_report.get("recommended_action", "TECHNICAL_REVIEW_REQUIRED")
        risk_idx = m5_report.get("risk_index", 0.5)
        if watchlist_res.get("is_flagged"):
            rec_action = "SECONDARY_INSPECTION_RECOMMENDED"
            risk_idx = max(risk_idx, 0.95)

        # ---------------------------------------------------------
        # Step 7: Module 6 Tamper-Evident SHA-256 Audit Logging
        # ---------------------------------------------------------
        audit_log = database_sync_service.log_inspection(
            recommended_action=rec_action,
            risk_index=risk_idx,
            doc_number=doc_num,
            officer_id=off_id,
            checkpoint_id=cp_id
        )

        total_latency = (time.perf_counter() - start_time) * 1000.0

        # Extract visual vs MRZ conflicts
        visual_mrz_conflicts = []
        if m2_report and isinstance(m2_report.get("conflicts"), list):
            visual_mrz_conflicts = m2_report.get("conflicts", [])
        elif m1_report and isinstance(m1_report.get("consistency", {}).get("conflicts"), list):
            visual_mrz_conflicts = m1_report.get("consistency", {}).get("conflicts", [])

        return UnifiedScreeningDossier(
            screening_id=screening_id,
            timestamp=now_iso,
            document_type=doc_type,
            recommended_action=rec_action,
            risk_index=round(risk_idx, 4),
            confidence_score=m5_report.get("confidence_score", 0.95),
            executive_summary=m5_report.get("executive_summary", ""),
            actionable_guidance=m5_report.get("actionable_guidance", ""),
            is_flagged_on_watchlist=watchlist_res.get("is_flagged", False),
            watchlist_details=watchlist_res.get("record"),
            extracted_fields=m1_report.get("fields", {}) if m1_report else {},
            mrz=m1_report.get("mrz") if m1_report else None,
            visual_mrz_conflicts=visual_mrz_conflicts,
            itemized_evidence=m5_report.get("itemized_evidence", {}),
            dimensional_risks=m5_report.get("dimensional_risks", {}),
            modules_telemetry=telemetry,
            audit_log=audit_log,
            total_latency_ms=round(total_latency, 2),
            errors=errors,
            warnings=warnings
        )
