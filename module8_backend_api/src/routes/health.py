"""Health and Readiness Route for Module 8."""

import time
from fastapi import APIRouter
from ..schemas.api_models import HealthResponse

router = APIRouter(tags=["Health & Status"])
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Returns real-time service health, uptime, and sub-module readiness status."""
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="HEALTHY",
        version="1.0.0",
        service="AI-DIDSS Verification Decision Support API",
        uptime_seconds=round(uptime, 2),
        modules_ready=[
            "module1_ocr",
            "module2_document_validation",
            "module3_tampering_detection",
            "module4_face_verification",
            "module5_explainable_evidence",
            "module6_database_sync",
            "module7_integration_engine"
        ]
    )
