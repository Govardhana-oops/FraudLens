# AI-DIDSS Module 3: Interface Contract & Integration Specification

**Module:** `module3_tampering_detection` (Module 3: Document Forensic & Tampering Detection Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Input Contract Schema

The interface accepts either:
1. `image`: raw image file path (str), raw image bytes (`bytes`), or numpy ndarray (`uint8`, RGB/BGR).
2. `regions` (optional): dictionary of bounding boxes from Module 1 OCR (e.g. `{"photo": [ymin, xmin, ymax, xmax], "mrz": [...]}`).

```python
from src.interface import tampering_detector

# Execution
report = tampering_detector.analyze(image_input, regions=optional_regions)
```

---

## 2. Output Contract Schema (to Downstream Modules 5, 7, 8)

```json
{
  "module": "module3_tampering_detection",
  "module_version": "1.0.0",
  "status": "NO_TAMPERING_EVIDENCE",
  "anomaly_score": 0.12,
  "confidence": 0.95,
  "indicators": {
    "ela_anomaly_score": 0.08,
    "noise_inconsistency_score": 0.14,
    "edge_gradient_discontinuity_score": 0.10,
    "spectral_fft_score": 0.05,
    "font_texture_score": 0.11
  },
  "suspicious_regions": [],
  "tampering_types_detected": [],
  "warnings": [],
  "errors": [],
  "review_required": false,
  "metadata": {
    "image_width": 1024,
    "image_height": 768,
    "color_channels": 3,
    "processing_time_ms": 12.4
  }
}
```
