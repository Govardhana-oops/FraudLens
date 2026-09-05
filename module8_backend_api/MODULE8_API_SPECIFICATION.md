# AI-DIDSS Module 8: OpenAPI REST Endpoints Specification

**Module:** `module8_backend_api` (Module 8: Verification Decision Support Backend API)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Endpoints Specification

### 1. Multi-Modal Document Inspection
* **Method:** `POST`
* **Route:** `/api/v1/screening/inspect`
* **Consumes:** `multipart/form-data`
* **Form Fields:**
  * `document_file`: UploadFile (JPEG / PNG image)
  * `live_face_file`: Optional[UploadFile] (Live probe selfie)
  * `officer_id`: Optional[str]
  * `checkpoint_id`: Optional[str]
* **Returns:** `200 OK` with `UnifiedScreeningDossier`

### 2. Offline Watchlist Query
* **Method:** `GET`
* **Route:** `/api/v1/watchlist/check/{doc_number}`
* **Query Params:** `country_code` (Optional[str])
* **Returns:** `200 OK` with `WatchlistLookupResult`

### 3. Differential Delta Sync
* **Method:** `POST`
* **Route:** `/api/v1/sync/differential`
* **Body:** `{"delta_records": [...]}`
* **Returns:** `200 OK` with `SyncReport`

### 4. Tamper-Evident Audit Logs
* **Method:** `GET`
* **Route:** `/api/v1/audit/logs`
* **Query Params:** `limit` (int = 100), `verify_integrity` (bool = true)
* **Returns:** `200 OK` with list of chained audit records and cryptographic integrity status

### 5. Health & Readiness
* **Method:** `GET`
* **Route:** `/api/v1/health`
* **Returns:** `{"status": "HEALTHY", "uptime_seconds": 120.5, "version": "1.0.0"}`
