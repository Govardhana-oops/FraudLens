# AI-DIDSS Module 4: Interface Contract & Integration Specification

**Module:** `module4_face_verification` (Module 4: Biometric Face Verification & Match Quality Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Input Contract Schema

```python
from src.interface import face_verifier

# Analyze document portrait vs live selfie/camera capture
report = face_verifier.verify(document_image=doc_img, live_image=live_img)
```

Inputs can be file paths (str), image byte streams (`bytes`), PIL Images, or numpy ndarrays (`uint8`, RGB/BGR).

---

## 2. Output Contract Schema (to Downstream Modules 5, 7, 8)

```json
{
  "module": "module4_face_verification",
  "module_version": "1.0.0",
  "status": "MATCH",
  "similarity_score": 0.885,
  "confidence": 0.94,
  "quality_report": {
    "doc_portrait_quality": {
      "overall_quality": 0.92,
      "sharpness": 145.2,
      "illumination_uniformity": 0.90,
      "is_compliant": true
    },
    "live_portrait_quality": {
      "overall_quality": 0.95,
      "sharpness": 210.5,
      "illumination_uniformity": 0.94,
      "is_compliant": true
    }
  },
  "liveness_assessment": {
    "is_live": true,
    "liveness_score": 0.92,
    "attack_type_detected": null
  },
  "match_details": {
    "cosine_distance": 0.115,
    "operating_threshold": 0.72,
    "feature_dimensions": 128
  },
  "warnings": [],
  "errors": [],
  "review_required": false,
  "metadata": {
    "processing_time_ms": 34.5
  }
}
```
