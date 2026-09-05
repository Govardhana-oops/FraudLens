# AI-DIDSS Module 5: Interface Contract & Integration Specification

**Module:** `module5_explainable_evidence` (Module 5: Explainable Evidence & Anomaly Assessment Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Public API Interface

```python
from src.interface import evidence_fusion_engine

# Accepts dictionary containing outputs from modules 1, 2, 3, and 4
dossier = evidence_fusion_engine.assess(
    module1_report=m1_ocr_output,
    module2_report=m2_val_output,
    module3_report=m3_tamp_output,
    module4_report=m4_bio_output
)
```

---

## 2. Output Contract Schema (to Decision Support Backend / UI Console)

```json
{
  "module": "module5_explainable_evidence",
  "module_version": "1.0.0",
  "recommended_action": "CLEAR",
  "risk_index": 0.085,
  "confidence_score": 0.96,
  "dimensional_risks": {
    "document_syntactic_risk": 0.05,
    "physical_tampering_risk": 0.10,
    "biometric_identity_risk": 0.11
  },
  "executive_summary": "Document structurally valid, no physical tampering detected, biometric face match verified with high confidence.",
  "itemized_evidence": {
    "positive_findings": [
      "All ICAO Doc 9303 checksums recalculated and verified valid.",
      "No compression or noise variance anomalies detected on bearer photo.",
      "Facial biometric match verified against live capture (similarity: 0.89)."
    ],
    "negative_findings": [],
    "uncertainties": []
  },
  "actionable_guidance": "Standard clearance recommended.",
  "review_required": false,
  "metadata": {
    "modules_fused": ["module1_ocr", "module2_document_validation", "module3_tampering_detection", "module4_face_verification"],
    "processing_time_ms": 4.2
  }
}
```
