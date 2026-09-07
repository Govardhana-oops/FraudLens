"""Document Inspection & Screening Route for Module 8."""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import numpy as np
import cv2

# Import integration orchestrator
from module7_integration_engine.src.interface import screening_orchestrator

router = APIRouter(tags=["Screening & Inspection"])

def _read_upload_image(file_bytes: bytes) -> Optional[np.ndarray]:
    if not file_bytes:
        return None
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is not None:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return None

@router.post("/screening/inspect")
async def inspect_document(
    document_file: Optional[UploadFile] = File(None, description="Image of document to inspect"),
    document_image: Optional[UploadFile] = File(None, description="Alias for document image"),
    live_face_file: Optional[UploadFile] = File(None, description="Optional live probe selfie"),
    face_image: Optional[UploadFile] = File(None, description="Alias for live face selfie"),
    document_type: Optional[str] = Form(None, description="Optional document type e.g. PASSPORT, NATIONAL_ID, DRIVERS_LICENSE"),
    capture_mode: Optional[str] = Form(None, description="Optional capture mode e.g. LIVE_CAMERA, UPLOAD_FILE"),
    face_capture_mode: Optional[str] = Form(None, description="Optional face capture mode e.g. LIVE_LIVENESS_CAMERA, UPLOAD_PHOTO"),
    officer_id: Optional[str] = Form(None),
    checkpoint_id: Optional[str] = Form(None)
):
    """Performs full multi-modal screening pipeline and returns unified explainable dossier."""
    # Resolve document file from either alias
    doc_target = document_file or document_image
    if doc_target is None:
        raise HTTPException(status_code=400, detail="Missing document image. Please provide document_file or document_image.")

    doc_bytes = await doc_target.read()
    doc_img = _read_upload_image(doc_bytes)

    if doc_img is None:
        raise HTTPException(status_code=400, detail="Invalid document image format or empty file.")

    # Resolve live face file from either alias
    face_target = live_face_file or face_image
    live_img = None
    if face_target:
        live_bytes = await face_target.read()
        live_img = _read_upload_image(live_bytes)

    try:
        dossier = screening_orchestrator.process_screening(
            document_image=doc_img,
            live_face_image=live_img,
            officer_id=officer_id or "CP-0082",
            checkpoint_id=checkpoint_id or "GATE-04"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Screening processing failure: {str(e)}")

    dossier_dict = dossier.model_dump() if hasattr(dossier, "model_dump") else (dossier.dict() if hasattr(dossier, "dict") else dict(dossier))

    # Attach detailed Module 4 Biometric verification report if live probe was submitted
    if live_img is not None:
        try:
            from module4_face_verification.src.interface import face_verifier
            m4_report = face_verifier.verify(doc_img, live_img)
            status_val = m4_report.get("status")
            status_str = status_val.value if hasattr(status_val, "value") else str(status_val)
            liveness = m4_report.get("liveness_assessment")
            liveness_dict = liveness if isinstance(liveness, dict) else (liveness.model_dump() if hasattr(liveness, "model_dump") else (liveness.dict() if hasattr(liveness, "dict") else None))
            liveness_score = float(liveness_dict.get("liveness_score", 0.0)) if liveness_dict else 0.0
            is_live = bool(liveness_dict.get("is_live", False)) if liveness_dict else False

            dossier_dict["face_comparison"] = {
                "matched": status_str == "MATCH",
                "status": status_str,
                "similarity_score": float(m4_report.get("similarity_score", 0.0)),
                "confidence": float(m4_report.get("confidence", 0.0)),
                "liveness_score": liveness_score,
                "liveness_detected": is_live,
                "threshold": float(m4_report.get("operating_threshold", 0.72)),
                "method": "Module 4 Biometric Verification",
                "doc_portrait_quality": m4_report.get("doc_portrait_quality"),
                "live_portrait_quality": m4_report.get("live_portrait_quality"),
                "liveness_assessment": liveness_dict,
                "cosine_distance": float(m4_report.get("cosine_distance", 1.0)) if m4_report.get("cosine_distance") is not None else 1.0,
                "review_required": bool(m4_report.get("review_required", True)),
                "warnings": m4_report.get("warnings", []),
                "errors": m4_report.get("errors", [])
            }
        except Exception as e:
            print("M4 Biometrics attaching error:", e)

    # Attach capture metadata
    if "metadata" not in dossier_dict or dossier_dict["metadata"] is None:
        dossier_dict["metadata"] = {}
    dossier_dict["metadata"]["capture_mode"] = capture_mode or "STANDARD"
    dossier_dict["metadata"]["face_capture_mode"] = face_capture_mode or ("LIVE_PROBE" if live_img is not None else "NONE")
    if document_type:
        dossier_dict["metadata"]["client_document_type"] = document_type

    return dossier_dict

@router.post("/biometrics/verify")
async def verify_biometrics(
    document_file: Optional[UploadFile] = File(None, description="Document image or extracted face"),
    document_image: Optional[UploadFile] = File(None, description="Alias for document image"),
    live_face_file: Optional[UploadFile] = File(None, description="Live traveler camera capture"),
    face_image: Optional[UploadFile] = File(None, description="Alias for live face"),
):
    """Direct 1:1 Biometric Face Verification endpoint using Module 4."""
    doc_target = document_file or document_image
    face_target = live_face_file or face_image

    if not doc_target or not face_target:
        raise HTTPException(status_code=400, detail="Both document_file and live_face_file must be provided.")

    doc_bytes = await doc_target.read()
    doc_img = _read_upload_image(doc_bytes)
    live_bytes = await face_target.read()
    live_img = _read_upload_image(live_bytes)

    if doc_img is None or live_img is None:
        raise HTTPException(status_code=400, detail="Invalid image format or empty file provided.")

    try:
        from module4_face_verification.src.interface import face_verifier
        m4_report = face_verifier.verify(doc_img, live_img)
        status_val = m4_report.get("status")
        status_str = status_val.value if hasattr(status_val, "value") else str(status_val)
        liveness = m4_report.get("liveness_assessment")
        liveness_dict = liveness if isinstance(liveness, dict) else (liveness.model_dump() if hasattr(liveness, "model_dump") else (liveness.dict() if hasattr(liveness, "dict") else None))
        liveness_score = float(liveness_dict.get("liveness_score", 0.0)) if liveness_dict else 0.0
        is_live = bool(liveness_dict.get("is_live", False)) if liveness_dict else False

        return {
            "matched": status_str == "MATCH",
            "status": status_str,
            "similarity_score": float(m4_report.get("similarity_score", 0.0)),
            "confidence": float(m4_report.get("confidence", 0.0)),
            "liveness_score": liveness_score,
            "liveness_detected": is_live,
            "threshold": float(m4_report.get("operating_threshold", 0.72)),
            "method": "Module 4 Biometric Verification",
            "doc_portrait_quality": m4_report.get("doc_portrait_quality"),
            "live_portrait_quality": m4_report.get("live_portrait_quality"),
            "liveness_assessment": liveness_dict,
            "cosine_distance": float(m4_report.get("cosine_distance", 1.0)) if m4_report.get("cosine_distance") is not None else 1.0,
            "review_required": bool(m4_report.get("review_required", True)),
            "warnings": m4_report.get("warnings", []),
            "errors": m4_report.get("errors", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Biometric verification failure: {str(e)}")

