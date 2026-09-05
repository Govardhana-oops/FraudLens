# Stage 7: Dedicated External Unseen-Data Test Plan

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-02  
**Frozen Model Target:** `LayoutAware-MultiScale-OCR-v2.0`  
**Evaluation Mode:** STRICTLY FROZEN (No training, no tuning, no rule changes)  

---

## 1. External Dataset Identity & Source

* **Dataset Identifier:** `SynthID-Doc-External v1.0`
* **Source & Licensing:** Generated under strict synthetic identity schemas for AI-DIDSS border screening evaluation (Zero unauthorized real identity documents).
* **Sample Count:** 30 document images across 15 distinct document identities.
* **Document Class Distribution:**
  * **Passports (ICAO TD3):** 6 samples (20%)
  * **Travel Visas (ICAO MRV-A):** 6 samples (20%)
  * **Driver's Licenses (AAMVA):** 6 samples (20%)
  * **National IDs (ICAO TD1):** 6 samples (20%)
  * **Residence Permits:** 6 samples (20%)

---

## 2. Frozen Pipeline Architecture

```text
External Document Image (Unseen)
      ↓
Quality Verification (Laplacian Blur & Glare Assessment)
      ↓
Standard Preprocessing (LAB CLAHE + Hough Line Deskew + Perspective Warp)
      ↓
Multi-Scale ROI Segmentation (Header, VIZ, MRZ 1.5x Upscaling, Photo)
      ↓
Optical Engine & MRZ Parser (ICAO Doc 9303 Modulo-10 Checksum)
      ↓
Document Type Classifier (Multi-Cue Visual & MRZ Geometry, Threshold = 0.50)
      ↓
Layout-Aware Spatial Field Extractor (Bidirectional MRZ/VIZ Cross-Fusion)
      ↓
Field Normalizer & Character Disambiguator (ISO 8601 YYYY-MM-DD, ISO 3166-1 Alpha-3)
      ↓
Field Validator (Chronological Logic & Cross-Field Conflict Engine)
      ↓
Standardized Structured JSON Output
```

---

## 3. Evaluation Dimensions & Protocols

1. **OCR-Level Performance:** CER, WER, Mean/Median Latency, Processing Throughput.
2. **Document-Type Classification:** Accuracy, Precision, Recall, F1, and Multi-Class Confusion Matrix.
3. **Field-Level Extraction:** Precision, Recall, F1, Exact Match, Normalized Match, UNKNOWN Rate, and REVIEW_REQUIRED Rate across all documented fields.
4. **MRZ Verification:** Detection rate, Parsing accuracy, Modulo-10 checksum pass rate, and Cross-Field conflict rate.
5. **Generalization Gap Analysis:** Direct metric delta between Internal Held-Out Test Set (Stage 6) and External Unseen Test Set (Stage 7).
6. **No-Tuning Rule:** The pipeline parameters (optimal confidence threshold = $0.50$, CLAHE clip limit = $2.0$) were determined exclusively during internal development and will NOT be tuned to the external dataset.
