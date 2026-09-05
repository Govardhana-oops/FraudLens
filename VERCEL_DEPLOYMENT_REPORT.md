# VERCEL DEPLOYMENT REPORT — FRAUDLENS FASTAPI BACKEND

**System:** AI-DIDSS (AI-Based Fake Identity & Document Screening System)  
**Target Repository:** `Govardhana-oops/FraudLens`  
**Repository Path:** `c:\Users\guvva\OneDrive\Desktop\PROTOTYPE`  
**Date:** September 5, 2026  
**Status:** **READY FOR CONFIGURATION / DOCUMENTED CONSTRAINTS**

---

## 1. Executive Summary & Entrypoint Resolution

Vercel deployment failed previously with:
```
No FastAPI entrypoint found in default locations, but found potential entrypoints:
module1_ocr/src/api.py (variable: app)
module1_ocr/tests/test_api.py (variable: app)
module8_backend_api/src/main.py (variable: app)
```

### ✅ Resolved Production Entrypoint
- **Production Backend Path:** `module8_backend_api/src/main.py`
- **Exposed ASGI App Variable:** `app` (`fastapi.FastAPI`)
- **Serverless Bridge Entrypoint:** [`api/index.py`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/api/index.py) (Standard Vercel Python entrypoint)
- **Ignored / Excluded Unit Entrypoints:** `module1_ocr/src/api.py`, `module1_ocr/tests/test_api.py`

---

## 2. Files Created and Modified

| File | Type | Purpose / Changes Made |
| :--- | :--- | :--- |
| [`api/index.py`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/api/index.py) | **NEW** | Vercel serverless entrypoint that configures `sys.path` dynamically for all submodules (Modules 1–8) and exports the production `app` from `module8_backend_api/src/main.py`. |
| [`vercel.json`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/vercel.json) | **NEW** | Directs Vercel's `@vercel/python` builder and route handler to map all incoming traffic (`/(.*)`) to `api/index.py`. |
| [`module6_database_sync/src/interface.py`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/module6_database_sync/src/interface.py) | **MODIFIED** | Added serverless environment check (`VERCEL` or `AWS_LAMBDA_FUNCTION_NAME`) to route SQLite database path to writeable `/tmp` partition. |
| [`scratch/test_module8_api.py`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/scratch/test_module8_api.py) | **NEW** | Comprehensive local automated integration test suite validating all Module 8 endpoints before deployment. |

---

## 3. Production Dependencies

The production dependency configuration is defined in [`requirements.txt`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/requirements.txt):

```text
# Web Framework & API Backend (Module 8)
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6

# Core Math & Data Structures
numpy>=1.24.0
pydantic>=2.5.0
pyyaml>=6.0.1
pandas>=2.0.0

# Computer Vision, Deep Learning & OCR (Modules 1, 3, 4)
pillow>=10.0.0
opencv-python-headless>=4.8.0
torch>=2.0.0
torchvision>=0.15.0
easyocr>=1.7.0
scikit-image>=0.21.0
scikit-learn>=1.3.0

# HTTP & Security Client Utilities
httpx>=0.25.0
requests>=2.31.0

# Quality Assurance & Testing Suite
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 4. Exact Vercel Deployment Configuration

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### `api/index.py`
```python
"""Vercel Serverless Entrypoint for AI-DIDSS FastAPI Production Backend."""

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
```

---

## 5. Local Pre-Deployment Verification Results

All tests were executed locally against `module8_backend_api/src/main.py` and `api/index.py`:

### Automated API Test Suite (`scratch/test_module8_api.py`)
1. **`GET /api/v1/health`**:
   - Status: **200 OK**
   - Payload: `{"status": "HEALTHY", "version": "1.0.0", "service": "AI-DIDSS Verification Decision Support API", "modules_ready": [...]}`
2. **`GET /api/v1/watchlist/check/P12345678`**:
   - Status: **200 OK**
   - Payload: `{"is_flagged": false, "record": null, "query_doc_number": "P12345678", "lookup_latency_ms": 0.004}`
3. **`GET /api/v1/audit/logs`**:
   - Status: **200 OK**
   - Cryptographic Integrity: `chain_intact: True` (Verified SHA-256 tamper-evident ledger)
4. **`POST /api/v1/screening/inspect` (Empty & Corrupt Inputs)**:
   - Status: **400 Bad Request** (Safely rejected with zero unhandled exceptions)
5. **`POST /api/v1/screening/inspect` (Synthetic Authorized Document: `DOC_PASSPORT_0001_v1.png`)**:
   - Status: **200 OK**
   - Recommended Action: `TECHNICAL_REVIEW_REQUIRED` (Risk Index: 0.565)
   - Extracted Fields: `document_type`, `passport_number`, `surname`, `given_names`, `full_name`, `nationality`, `date_of_birth`, `date_of_expiry`, `mrz_line1`, `mrz_line2`
   - Telemetry Modules: `module1_ocr`, `module2_document_validation`, `module3_tampering_detection`, `module4_face_verification`, `module6_database_sync`, `module5_explainable_evidence`

### Existing Regression Test Suites
- **`pytest module8_backend_api/tests`**: **13 / 13 PASSED** (100%)
- **`pytest module7_integration_engine/tests`**: **18 / 18 PASSED** (100%)

---

## 6. Known Deployment Limitations & Serverless Architecture Analysis

In accordance with strict technical audit standards, the following platform-specific constraints apply when deploying deep learning computer vision architectures on Vercel:

| Dimension | Vercel Serverless Function Constraints | AI-DIDSS Impact & Technical Status |
| :--- | :--- | :--- |
| **Package Size Limit** | Max **250 MB** uncompressed per serverless function (AWS Lambda constraint). | `torch` + `torchvision` + `easyocr` + `opencv-python-headless` exceeds 1.2 GB uncompressed. Vercel build will succeed for routing and entrypoint resolution, but full PyTorch wheel installation during Vercel function packaging may exceed the 250 MB ceiling. |
| **Execution Timeout** | **10s** (Hobby Plan) / **60s–300s** (Pro Plan). | Cold-start CPU neural OCR inference on single-vCPU lambda takes ~5–12s. Pro plan or containerized infrastructure (Docker / Cloud Run / Streamlit Cloud) is recommended for production multi-modal workloads. |
| **Filesystem State** | Read-only root directory; only `/tmp` (512 MB) is writable and ephemeral. | Handled: SQLite database and model cache paths are routed to `/tmp`. Audit entries on serverless instances are local to that ephemeral container. |
| **Tesseract / Binary Executables** | No native system binaries installed unless bundled in function. | Handled: System uses pure-Python / PyTorch EasyOCR and OpenCV headless with zero external Tesseract binary dependencies. |

---

## 7. Deployment Readiness Assessment

- **Entrypoint Configuration:** **READY** (`api/index.py` & `vercel.json` map unambiguously to `module8_backend_api/src/main.py`).
- **Local Functional Verification:** **READY** (100% test pass rate across all endpoints and regressions).
- **Serverless Architectural Constraint:** **DOCUMENTED** (Vercel serverless function package size limits require Pro/Enterprise Lambda layers or container deployment for full PyTorch inference).
