# FraudLens / AI-DIDSS — API Integration Contract & Specifications

This document outlines the real, verified FastAPI REST API endpoints exposed by `module8_backend_api` and consumed by the new React + Vite Frontend.

---

## Architecture Overview

```
[Browser / Client]
       │
       ▼
[Vercel Frontend (React 18 + Vite)]
       │ (VITE_API_BASE_URL: http://localhost:8000 or Render Backend URL)
       ▼
[Render FastAPI Backend (Module 8)]
       │
       ├─► Module 7 (Integration Engine Orchestrator)
       │      ├─► Module 1 (Multi-Engine Document OCR)
       │      ├─► Module 2 (Rule-Based Logic & ICAO Checksum Validation)
       │      ├─► Module 3 (Forensic Tampering & ELA Detection)
       │      ├─► Module 4 (Biometric 1:1 Face Verification & Liveness)
       │      └─► Module 5 (Explainable Evidence & Risk Assessment)
       │
       └─► Module 6 (Database Sync, SLTD Watchlist, Cryptographic SHA-256 Audit Ledger)
```

---

## Verified Backend Endpoints

### 1. Health & Readiness Diagnostics
- **Method**: `GET`
- **Path**: `/api/v1/health`
- **Description**: Returns the real-time operational status of the API gateway, system uptime, and readiness of all 7 core submodules.
- **Request Parameters**: None
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "HEALTHY",
    "version": "1.0.0",
    "service": "AI-DIDSS Verification Decision Support API",
    "uptime_seconds": 1284.52,
    "modules_ready": [
      "module1_ocr",
      "module2_document_validation",
      "module3_tampering_detection",
      "module4_face_verification",
      "module5_explainable_evidence",
      "module6_database_sync",
      "module7_integration_engine"
    ]
  }
  ```
- **Error Response**:
  - `503 Service Unavailable`: Backend service or submodules offline.

---

### 2. Document Inspection & Multi-Modal Screening Pipeline
- **Method**: `POST`
- **Path**: `/api/v1/screening/inspect`
- **Description**: Ingests document image and optional companion live probe photo. Executes the end-to-end multi-engine OCR, MRZ validation, forensic tampering detection, biometric comparison, watchlist lookup, and SHA-256 audit ledger logging.
- **Content-Type**: `multipart/form-data`
- **Request Parameters (Form Data)**:
  - `document_file` (`File`, required): Image binary of the ID / passport / visa document.
  - `live_face_file` (`File`, optional): Live traveler face probe image for 1:1 biometric matching.
  - `document_type` (`string`, optional): e.g. `"PASSPORT"`, `"VISA"`, `"NATIONAL_ID"`, `"RESIDENCE_PERMIT"`, `"DRIVER_LICENSE"`, `"AUTO_DETECT"`.
  - `capture_mode` (`string`, optional): e.g. `"UPLOAD_FILE"`, `"LIVE_CAMERA"`.
  - `face_capture_mode` (`string`, optional): e.g. `"LIVE_LIVENESS_CAMERA"`, `"UPLOAD_PHOTO"`.
  - `officer_id` (`string`, optional): ID of the inspecting border officer. Default: `"CP-0082"`.
  - `checkpoint_id` (`string`, optional): Identifier of the inspection terminal. Default: `"GATE-04"`.
- **Success Response (`200 OK`)**:
  ```json
  {
    "screening_id": "SCR-20260906-8A3F",
    "timestamp": "2026-09-06T10:15:30Z",
    "status": "VALID",
    "confidence_score": 0.98,
    "document_type": "PASSPORT",
    "document_number": "L898902C3",
    "record_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "officer_id": "CP-0082",
    "checkpoint_id": "GATE-04",
    "processing_time_ms": 320,
    "extracted_fields": [
      {
        "field_name": "Document Number",
        "extracted_value": "L898902C3",
        "confidence": 0.99,
        "engine": "EasyOCR / Tesseract Hybrid"
      },
      {
        "field_name": "Surname",
        "extracted_value": "UTOPIA",
        "confidence": 0.98,
        "engine": "EasyOCR"
      },
      {
        "field_name": "Given Names",
        "extracted_value": "ERIK",
        "confidence": 0.97,
        "engine": "EasyOCR"
      },
      {
        "field_name": "Nationality",
        "extracted_value": "UTO",
        "confidence": 0.99,
        "engine": "MRZ Parser"
      },
      {
        "field_name": "Date of Expiry",
        "extracted_value": "2031-08-12",
        "confidence": 0.98,
        "engine": "MRZ Parser"
      }
    ],
    "validation_checks": [
      {
        "rule_id": "MRZ_CHECKSUM_DOC_NO",
        "description": "Document number ICAO 7-3-1 check digit verification",
        "result": "PASS",
        "severity": "CRITICAL"
      },
      {
        "rule_id": "DOC_EXPIRY_CHECK",
        "description": "Verification that document expiration date is in the future",
        "result": "PASS",
        "severity": "CRITICAL"
      }
    ],
    "tampering_analysis": {
      "tampering_score": 0.04,
      "tampering_detected": false,
      "ela_disparity_score": 0.03,
      "copy_move_detected": false,
      "font_anomaly_score": 0.05,
      "anomalies_found": []
    },
    "face_comparison": {
      "matched": true,
      "similarity_score": 0.94,
      "liveness_score": 0.97,
      "liveness_detected": true,
      "threshold": 0.75,
      "method": "ArcFace / DLIB Biometric Pipeline"
    },
    "watchlist_result": {
      "hit": false,
      "database_checked": "INTERPOL_SLTD_NATIONAL",
      "matched_entries": []
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: `{"detail": "Missing document image. Please provide document_file or document_image."}`
  - `422 Unprocessable Entity`: Invalid upload parameters or corrupt image bytes.
  - `500 Internal Server Error`: Pipeline exception in underlying submodules.

---

### 3. Cryptographic Audit Log Ledger & Chain Integrity
- **Method**: `GET`
- **Path**: `/api/v1/audit/logs`
- **Description**: Retrieves recorded audit journal entries and computes SHA-256 Merkle chain continuity and cryptographic integrity.
- **Query Parameters**:
  - `limit` (`integer`, optional, default `100`, min `1`, max `1000`): Maximum entries to return.
  - `verify_integrity` (`boolean`, optional, default `true`): Whether the backend should mathematically verify SHA-256 chain linkage.
- **Success Response (`200 OK`)**:
  ```json
  {
    "total_logs": 24,
    "chain_intact": true,
    "logs": [
      {
        "sequence_number": 1,
        "log_id": "LOG-20260906-0001",
        "timestamp": "2026-09-06T09:00:00Z",
        "event_type": "SYSTEM_STARTUP",
        "officer_id": "SYSTEM",
        "checkpoint_id": "GATE-04",
        "doc_number": "SYSTEM_INIT",
        "recommended_action": "INITIALIZE",
        "risk_index": 0.0,
        "current_hash": "4a53c303287e1b5d6a61bbf8e9acf67ac2c4b878134d30fc978b6ff12f8616a2",
        "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000"
      }
    ]
  }
  ```
- **Error Response**:
  - `500 Internal Server Error`: Database ledger read failure.

---

### 4. Differential Synchronization
- **Method**: `POST`
- **Path**: `/api/v1/sync/differential`
- **Description**: Executes two-way differential synchronization between the local inspection terminal SQLite store and the Central Immigration HQ cloud.
- **Request Body (`application/json`)**:
  ```json
  {
    "delta_records": []
  }
  ```
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "SUCCESS",
    "synced_records": 12,
    "last_sync_timestamp": "2026-09-06T10:18:45Z",
    "watchlist_version": "2026.09.06.01"
  }
  ```

---

### 5. Offline SLTD & Watchlist Check
- **Method**: `GET`
- **Path**: `/api/v1/watchlist/check/{doc_number}`
- **Description**: Sub-millisecond indexed lookup against local Stolen and Lost Travel Document (SLTD) and revocation records.
- **Path Parameters**:
  - `doc_number` (`string`, required): Document number to query.
- **Query Parameters**:
  - `country_code` (`string`, optional): 3-letter ISO 3166-1 alpha-3 code.
- **Success Response (`200 OK`)**:
  ```json
  {
    "doc_number": "L898902C3",
    "hit": false,
    "reason": null,
    "severity": "NONE"
  }
  ```

---

## Frontend Source-of-Truth Enforcement

1. **Zero Hardcoded Values**: All counters, latency calculations, confidence percentages, and audit logs are derived directly from active API responses and the local database state.
2. **Backend Truth Replacement**: Upon completing a screening, the frontend receives the full response from `/api/v1/screening/inspect`, commits it to the local store, and recomputes all dashboard statistics dynamically.
3. **Graceful Connection Handling**: When the backend is offline, the frontend displays clear disconnected statuses and allows offline buffer viewing rather than fabricating mock data.
