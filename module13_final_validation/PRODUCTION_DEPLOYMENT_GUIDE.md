# AI-DIDSS Production Deployment & Runbook Guide

**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Version:** `v1.0.0-PRODUCTION-READY`  
**Date:** 2026-09-03  

---

## 1. Quickstart Commands

### 1. Execute Submodule Readiness Check
```powershell
python -m module13_final_validation.src.cli check
```

### 2. Screen an Identity Document Scan via CLI
```powershell
python -m module13_final_validation.src.cli screen --image path/to/passport.jpg
```

### 3. Launch Backend Decision API Server
```powershell
uvicorn module8_backend_api.src.main:app --host 0.0.0.0 --port 8000
```

### 4. Serve Officer Inspection Console UI
```powershell
python -m http.server 3000 --directory module9_officer_console
```

### 5. Run Global Master System Test Suite (359 Tests)
```powershell
pytest module1_ocr/ module2_document_validation/ module3_tampering_detection/ module4_face_verification/ module5_explainable_evidence/ module6_database_sync/ module7_integration_engine/ module8_backend_api/ module9_officer_console/ module10_system_test_matrix/ module11_performance_profiling/ module12_security_audit/ module13_final_validation/ -p no:cacheprovider
```
