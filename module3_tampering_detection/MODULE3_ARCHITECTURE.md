# AI-DIDSS Module 3: Document Tampering & Physical Anomaly Detection Architecture

**Module:** `module3_tampering_detection` (Module 3: Document Forensic & Tampering Detection Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Stage:** Stage 1 — Architecture & Threat Modeling  
**Date:** 2026-09-03  

---

## 1. Executive Summary & Purpose

Module 3 is a multi-modal digital image forensics and physical anomaly analysis engine. It ingests raw document images (along with bounding regions identified by Module 1 OCR) and evaluates evidence of digital manipulation, physical alteration, splicing, photo substitution, and text tampering.

### Strict Decision-Support Mandate
> [!IMPORTANT]
> **Module 3 produces objective forensic evidence maps and anomaly scores, NOT criminal fraud convictions.**  
> A high anomaly score indicates statistical, spectral, or compression inconsistencies (e.g. image re-saving or photo splicing) for human forensic officer review. Module 3 **NEVER outputs `FRAUD`, `CRIMINAL`, `DETAIN`, or `FORGERY`**.

---

## 2. Multi-Layer Forensic Pipeline Architecture

```
                       [ Input Document Image (RGB) ]
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
     [ Forensic Preprocessor ]                     [ Region Localization ]
     ├── Dimension & Color Check                   ├── Portrait Photo Box
     ├── Metadata & Header Scan                    ├── MRZ Band
     └── Colorspace Decomposition                  └── Text Field Regions
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
                   [ Multi-Modal Forensic Detectors ]
    ┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
    ▼                         ▼                         ▼                         ▼
[ 1. ELA Detector ]    [ 2. Noise Variance ]    [ 3. Edge/Splicing ]   [ 4. FFT Spectral ]
  Compression residue    Wavelet / High-freq      Gradient jump at       Periodic grid &
  error discrepancy      variance mapping         bounding borders       resampling peaks
    │                         │                         │                         │
    └─────────────────────────┼─────────────────────────┴─────────────────────────┘
                              ▼
                 [ Explainable Forensic Fusion ]
                 ├── Weighted Anomaly Aggregation
                 ├── Suspicious Region Bounding Map
                 └── Confidence-Calibrated Decision Logic
                              │
                              ▼
              [ Standardized Tampering Evidence Report ]
              ├── Status: NO_TAMPERING_EVIDENCE / POTENTIAL_TAMPERING / REVIEW_REQUIRED
              ├── Overall Anomaly Score: [0.0, 1.0]
              ├── Forensic Indicator Heatmaps & Bounding Boxes
              └── Explainable Audit Telemetry
```

---

## 3. Core Forensic Detection Modalities

1. **Error Level Analysis (ELA):** Analyzes compression error differentials across different compression grids to detect spliced or independently saved image elements.
2. **Noise Inconsistency Analysis (NIA):** Analyzes residual high-frequency noise variance across document sub-regions (a spliced photo or pasted text patch exhibits a distinct noise distribution compared to the substrate).
3. **Edge & Gradient Discontinuity Analysis (EDA):** Measures artificial gradient steps, copy-move boundaries, and unnatural clipping around portrait borders and text characters.
4. **Spectral & Frequency Analysis (2D FFT):** Detects periodic interpolation peaks, lattice artifacts, screen capture moiré patterns, and resampling grids.
5. **Text & Font Inconsistency Analysis:** Evaluates stroke thickness, anti-aliasing uniformity, and background micro-pattern disruption.

---

## 4. Status Taxonomy & Semantic Precedence

$$\text{INVALID\_INPUT} \succ \text{PROCESSING\_ERROR} \succ \text{UNKNOWN} \succ \text{POTENTIAL\_TAMPERING} \succ \text{REVIEW\_REQUIRED} \succ \text{NO\_TAMPERING\_EVIDENCE}$$

* **`NO_TAMPERING_EVIDENCE`**: All forensic indicators within normal baseline variation ($\text{Anomaly Score} < 0.35$).
* **`REVIEW_REQUIRED`**: Minor anomalies, severe image blur, high compression artifacts, or partial region occlusion ($0.35 \le \text{Anomaly Score} < 0.65$).
* **`POTENTIAL_TAMPERING`**: Statistically significant, localized forensic anomalies across multiple modalities (e.g. photo border splicing + ELA spike) ($\text{Anomaly Score} \ge 0.65$).
* **`UNKNOWN`**: Image quality too degraded or resolution too low to extract reliable forensic features.
* **`INVALID_INPUT`**: Corrupted image bytes or unreadable image buffer.
