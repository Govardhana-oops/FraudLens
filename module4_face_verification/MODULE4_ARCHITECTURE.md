# AI-DIDSS Module 4: Biometric Face Verification & Match Quality Architecture

**Module:** `module4_face_verification` (Module 4: Biometric Face Verification & Match Quality Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Stage:** Stage 1 — Architecture & Biometric Standards  
**Date:** 2026-09-03  

---

## 1. Executive Summary & Purpose

Module 4 is a 1:1 biometric face verification and ICAO Doc 9303 portrait quality assessment engine. It compares the identity document bearer portrait (extracted from passport/ID by Module 1) against a live camera capture / probe image.

### Non-Autonomous Exclusion Mandate
> [!IMPORTANT]
> **Module 4 produces quantitative match scores and quality evidence for border officers, NOT autonomous border refusals.**  
> A biometric mismatch indicates facial feature variance beyond statistical match thresholds. Module 4 **NEVER outputs `IMPOSTER`, `CRIMINAL`, `DETAIN`, or `FORGER`**.

---

## 2. Multi-Stage Biometric Pipeline

```
   [ Document Portrait Crop ]             [ Live Camera / Probe Image ]
               │                                       │
               └───────────────────┬───────────────────┘
                                   ▼
                   [ Stage 1: Face Detection & BBox ]
                   ├── Haar / Multi-scale Face Cascade
                   └── Spatial Crop Normalization
                                   │
                                   ▼
                   [ Stage 2: ICAO Portrait Quality ]
                   ├── Sharpness (Laplacian Variance >= 20.0)
                   ├── Illumination Uniformity & Contrast
                   ├── Aspect Ratio & Head Tilt Bounds
                   └── Glare / Specular Reflection Detection
                                   │
                                   ▼
                   [ Stage 3: Presentation Attack Check (PAD) ]
                   ├── Screen Moiré & Texture Analysis
                   └── Printed Paper Boundary Clues
                                   │
                                   ▼
                   [ Stage 4: Feature Representation ]
                   ├── 128D Multi-Scale Normalized Gradient Embedding
                   └── Global Color & Spatial Histogram Moments
                                   │
                                   ▼
                   [ Stage 5: Calibrated Cosine Similarity ]
                   ├── Cosine Distance Computation
                   ├── Calibrated Similarity Score in [0.0, 1.0]
                   └── Operating Threshold (Match: >= 0.72)
                                   │
                                   ▼
                   [ Standardized Biometric Report ]
```

---

## 3. Status Taxonomy & Decision Logic

$$\text{INVALID\_INPUT} \succ \text{PROCESSING\_ERROR} \succ \text{NO\_FACE\_DETECTED} \succ \text{POOR\_QUALITY} \succ \text{SPOOF\_ATTEMPT\_DETECTED} \succ \text{NO\_MATCH} \succ \text{REVIEW\_REQUIRED} \succ \text{MATCH}$$

* **`MATCH`**: Both faces clear, quality compliant, similarity score $\ge 0.72$.
* **`NO_MATCH`**: Both faces high quality, but similarity score $< 0.50$ (indicates different person).
* **`REVIEW_REQUIRED`**: Borderline similarity score ($0.50 \le \text{Score} < 0.72$) or minor pose/illumination discrepancy.
* **`POOR_QUALITY`**: Severe blur, extreme lighting, or partial face occlusion preventing reliable matching.
* **`NO_FACE_DETECTED`**: No recognizable face found in either image.
* **`SPOOF_ATTEMPT_DETECTED`**: Significant presentation attack signatures (e.g. screen replay moiré).
