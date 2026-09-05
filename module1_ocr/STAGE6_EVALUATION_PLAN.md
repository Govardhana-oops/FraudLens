# Stage 6: Comprehensive Evaluation & Error Analysis Plan

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-02  
**Active Production Architecture:** `LayoutAware-MultiScale-OCR-v2.0`  
**Baseline Model:** `DocumentOCR-v1.0-baseline`  

---

## 1. Objectives & Scope

The objective of Stage 6 is to perform a rigorous, reproducible, multi-dimensional evaluation of the complete Module 1 OCR and document understanding pipeline on internal reserved partitions (`data/validation/` and `data/test/`) without touching or contaminating the isolated external test set (`data/external_test/`).

---

## 2. Dataset Boundaries & Split Partitioning

| Partition | Images Count | Document Identities | Split Share | Purpose | Leakage Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`data/train/`** | 168 | 84 | 70% | Spatial template fitting & dictionary calibration | Grouped by doc ID |
| **`data/validation/`** | 36 | 18 | 15% | Hyperparameter & confidence threshold selection | Zero group overlap |
| **`data/test/`** | 36 | 18 | 15% | Held-out internal performance benchmarking | Zero group overlap |
| **`data/external_test/`** | 30 | 15 | Isolated | **100% UNTOUCHED (Preserved for Stage 7)** | **STRICTLY QUARANTINED** |

---

## 3. Evaluation Dimensions & Metrics

### A. OCR-Level Metrics
* **Character Error Rate (CER):** Levenshtein edit distance on character tokens.
* **Word Error Rate (WER):** Word-level token edit distance.
* **Mean & Median Latency (ms):** Execution time on CPU (AMD Ryzen / Multi-threaded).
* **Throughput:** Processed documents per second.

### B. Document-Type Classification Metrics
* Accuracy, Macro Precision, Recall, F1.
* Multi-class Confusion Matrix across: `passport`, `visa`, `driver_license`, `national_id`, `permit`, `unknown_document`.

### C. Field-Level Extraction Metrics
* Field Precision, Recall, and F1-Score.
* Exact Match Ratio & Normalized Exact Match Ratio.
* Extraction Failure Rate, UNKNOWN Rate, and REVIEW_REQUIRED Rate.
* Evaluated across core fields: `passport_number`, `visa_number`, `license_number`, `id_number`, `permit_number`, `full_name`, `date_of_birth`, `date_of_expiry`, `nationality`, `address`, `vehicle_class`.

### D. MRZ & Checksum Verification Metrics
* MRZ Detection Success Rate.
* ICAO Doc 9303 Checksum Valid / Invalid Ratio ($[7, 3, 1]$ modulo-10 weights).
* Visual vs MRZ Consistency & Evidentiary Conflict Rate.

### E. Confidence Calibration & Reliability
* Expected Calibration Error (ECE).
* Accuracy per Confidence Bin: $[0.0 - 0.2), [0.2 - 0.4), [0.4 - 0.6), [0.6 - 0.8), [0.8 - 1.0]$.
* Threshold Sensitivity Sweep ($0.50, 0.60, 0.70, 0.80, 0.90$).

---

## 4. Standardized Error Taxonomy

1. **Image Quality Errors:** Blur, glare overexposure, perspective distortion, low contrast.
2. **OCR Glyphic Errors:** Character substitution ($O \leftrightarrow 0, I \leftrightarrow 1$), character omissions, spacing artifacts.
3. **Field Extraction Errors:** Spatial proximity mismatch, multiline boundary overflow, missing visual anchor.
4. **Validation & Normalization Errors:** Ambiguous date parsing, chronological violation, non-standard country abbreviation.
5. **MRZ Evidentiary Conflicts:** Optical character read divergence between VIZ and MRZ lines.

---

## 5. Leakage Prevention Protocol

* Evaluation scripts will strictly reference `data/annotations/val_annotations.jsonl` and `data/annotations/test_annotations.jsonl`.
* `data/external_test/` directory path is strictly barred from all Stage 6 execution paths.
