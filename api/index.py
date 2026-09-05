"""Vercel Serverless Entrypoint for AI-DIDSS FastAPI Production Backend.

Explicitly resolves and exports the production FastAPI application instance
from module8_backend_api/src/main.py (app) for Vercel deployment.
"""

import os
import sys
from pathlib import Path

# Ensure repository root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure all AI-DIDSS submodules are on sys.path for direct module resolution
for m_dir in [
    "module1_ocr",
    "module2_document_validation",
    "module3_tampering_detection",
    "module4_face_verification",
    "module5_explainable_evidence",
    "module6_database_sync",
    "module7_integration_engine",
    "module8_backend_api"
]:
    p = str(ROOT_DIR / m_dir)
    if p not in sys.path:
        sys.path.insert(0, p)

# Configure writeable /tmp paths for serverless execution
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    os.environ.setdefault("TORCH_HOME", "/tmp/.cache/torch")
    os.environ.setdefault("EASYOCR_MODULE_PATH", "/tmp/.EasyOCR")

# Import and expose the production FastAPI app
from module8_backend_api.src.main import app
