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
    document_file: UploadFile = File(..., description="Image of document to inspect"),
    live_face_file: Optional[UploadFile] = File(None, description="Optional live probe selfie"),
    officer_id: Optional[str] = Form(None),
    checkpoint_id: Optional[str] = Form(None)
):
    """Performs full multi-modal screening pipeline and returns unified explainable dossier."""
    doc_bytes = await document_file.read()
    doc_img = _read_upload_image(doc_bytes)

    if doc_img is None:
        raise HTTPException(status_code=400, detail="Invalid document image format or empty file.")

    live_img = None
    if live_face_file:
        live_bytes = await live_face_file.read()
        live_img = _read_upload_image(live_bytes)

    dossier = screening_orchestrator.process_screening(
        document_image=doc_img,
        live_face_image=live_img,
        officer_id=officer_id,
        checkpoint_id=checkpoint_id
    )

    return dossier
