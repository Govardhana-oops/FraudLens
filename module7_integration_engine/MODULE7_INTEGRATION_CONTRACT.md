# AI-DIDSS Module 7: Interface Contract & Integration Specification

**Module:** `module7_integration_engine` (Module 7: Multi-Module Integration Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Public API Interface

```python
from src.interface import screening_orchestrator

# Processes complete multi-modal document and optional live face screening
dossier = screening_orchestrator.process_screening(
    document_image=doc_input,          # File path, numpy ndarray, or PIL Image
    live_face_image=live_probe_input,  # Optional live camera feed
    officer_id="OFFICER-007",
    checkpoint_id="AIRPORT-GATE-04"
)
```

---

## 2. Unified Screening Dossier Output Contract

```json
{
  "screening_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": "2026-09-03T14:40:00Z",
  "document_type": "passport",
  "recommended_action": "CLEAR",
  "risk_index": 0.082,
  "confidence_score": 0.96,
  "executive_summary": "All document validation checks, forensic tampering scans, and biometric match verifications passed successfully.",
  "actionable_guidance": "Standard clearance approved. No anomalies or discrepancies detected.",
  "is_flagged_on_watchlist": false,
  "modules_executed": {
    "module1_ocr": {"status": "SUCCESS", "latency_ms": 12.4},
    "module2_validation": {"status": "VALID", "latency_ms": 1.2},
    "module3_tampering": {"status": "NO_TAMPERING_EVIDENCE", "latency_ms": 28.5},
    "module4_biometrics": {"status": "MATCH", "latency_ms": 13.8},
    "module5_evidence": {"status": "SUCCESS", "latency_ms": 0.06},
    "module6_database": {"status": "SUCCESS", "latency_ms": 0.01}
  },
  "audit_log": {
    "log_id": "audit-uuid",
    "entry_hash": "sha256-hex",
    "prev_hash": "sha256-hex"
  },
  "total_latency_ms": 56.0
}
```
