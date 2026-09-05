# AI-DIDSS Module 8: Verification Decision Support Backend API

**Module:** `module8_backend_api` (Module 8: Verification Decision Support Backend API)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Status:** **`FROZEN (13/13 TESTS PASSED - 100%)`**  

---

## 1. Overview & Operational Philosophy

Module 8 provides an asynchronous FastAPI REST server hosting real-time screening, watchlist check, synchronization, and audit verification endpoints for border control workstations and web consoles.

### Available REST Endpoints

1. `POST /api/v1/screening/inspect`: Multipart file upload for full multi-modal document & live face screening.
2. `GET /api/v1/watchlist/check/{doc_number}`: Sub-millisecond offline SLTD query.
3. `POST /api/v1/sync/differential`: Two-way differential synchronization pass.
4. `GET /api/v1/audit/logs`: Cryptographically verified SHA-256 chained audit journal logs.
5. `GET /api/v1/health`: Real-time system health and module readiness probe.

---

## 2. How to Run Module 8

```powershell
cd module8_backend_api
pytest tests/ -v -p no:cacheprovider
```

To run the API server locally:
```powershell
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
