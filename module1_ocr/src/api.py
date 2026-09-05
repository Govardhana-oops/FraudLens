"""FastAPI REST API Service for AI-DIDSS Module 1: Document OCR & Understanding.

Endpoints:
- GET  /health      : Returns module health status and frozen model version.
- POST /ocr/analyze : Analyzes uploaded document image or image file path.
"""

import os
import sys
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.interface import document_ocr

app = FastAPI(
    title="AI-DIDSS Module 1: Document OCR & Understanding API",
    version="1.0.0",
    description="Identity and Travel Document OCR Extraction Service for Border Screening & KYC."
)

class AnalyzePathRequest(BaseModel):
    image_path: str
    metadata: Optional[dict] = None

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint providing module status and frozen version information."""
    return {
        "status": "healthy",
        "module": "module1_ocr",
        "module_version": document_ocr.module_version,
        "model_version": document_ocr.model_version
    }

@app.post("/ocr/analyze", status_code=status.HTTP_200_OK)
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None)
):
    """Processes document image and returns standardized structured extraction result."""
    try:
        if file is not None:
            contents = await file.read()
            if not contents:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "status": "INVALID_INPUT",
                        "error": "Uploaded file is empty (0 bytes)"
                    }
                )
            result = document_ocr.process(contents, metadata={"filename": file.filename})
            return JSONResponse(content=result)

        elif image_path is not None:
            if not os.path.exists(image_path):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "status": "INVALID_INPUT",
                        "error": f"Image file not found: {image_path}"
                    }
                )
            result = document_ocr.process(image_path)
            return JSONResponse(content=result)

        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "INVALID_INPUT",
                    "error": "Either multipart file upload or 'image_path' parameter is required."
                }
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "PROCESSING_ERROR",
                "error": f"Internal API processing exception: {str(e)}"
            }
        )

@app.post("/ocr/analyze_json", status_code=status.HTTP_200_OK)
def analyze_document_json(req: AnalyzePathRequest):
    """JSON-body endpoint accepting image file path."""
    if not os.path.exists(req.image_path):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "INVALID_INPUT",
                "error": f"Image file not found: {req.image_path}"
            }
        )
    result = document_ocr.process(req.image_path, metadata=req.metadata)
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
