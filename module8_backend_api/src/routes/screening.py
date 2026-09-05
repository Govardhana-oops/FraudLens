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

    dossier = screening_orchestrator.process_screening(
        document_image=doc_img,
        live_face_image=live_img,
        officer_id=officer_id or "CP-0082",
        checkpoint_id=checkpoint_id or "GATE-04"
    )

    # Attach capture metadata
    if "metadata" not in dossier:
        dossier["metadata"] = {}
    dossier["metadata"]["capture_mode"] = capture_mode or "STANDARD"
    dossier["metadata"]["face_capture_mode"] = face_capture_mode or ("LIVE_PROBE" if live_img is not None else "NONE")
    if document_type:
        dossier["metadata"]["client_document_type"] = document_type

    return dossier
