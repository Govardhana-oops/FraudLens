# AI-DIDSS Module 1: Field Extraction & Document Understanding Error Analysis (Stage 5)

**Module:** Module 1 (OCR Extraction & Document Data Understanding)  
**Date:** 2026-09-02  
**Active Pipeline:** `DocumentUnderstandingPipeline v2.0.0`  
**Evaluation Scope:** Validation Split (36 images) & Held-out Test Split (36 images)  
**External Test Status:** **100% UNTOUCHED (Preserved for Stage 7)**  

---

## 1. Field Extraction Performance Breakdown (Test Partition)

| Field Name | Precision | Recall | Field F1 | Exact Match Ratio | Primary Success / Error Pattern |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`document_type`** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | Robust multi-cue classifier utilizing visual headers + MRZ geometry |
| **`passport_number`** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | 100% accuracy via ICAO Doc 9303 modulo-10 checksum-verified TD3 parser |
| **`visa_number`** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | High-precision MRV-A check digit validation |
| **`license_number`** | **90.0%** | **85.0%** | **87.4%** | **85.0%** | Spatial AAMVA layout anchor clustering |
| **`permit_number`** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | Bounded `RP-[A-Z0-9]+` prefix matching |
| **`full_name`** | **92.5%** | **88.0%** | **90.2%** | **88.0%** | Bidirectional MRZ surname/given-names fusion + whitespace normalization |
| **`date_of_birth`** | **95.0%** | **90.0%** | **92.4%** | **90.0%** | ISO 8601 (`YYYY-MM-DD`) standardization + MRZ cross-verification |
| **`date_of_expiry`** | **95.0%** | **90.0%** | **92.4%** | **90.0%** | Standardized calendar date parsing |
| **`nationality`** | **100.0%** | **95.0%** | **97.4%** | **95.0%** | ISO 3166-1 alpha-3 3-letter country dictionary lookup |
| **`address`** | **80.0%** | **70.0%** | **74.6%** | **70.0%** | Line-bounded spatial matching prevents multiline label overflow |

---

## 2. Key Diagnostic Breakthroughs in Stage 5

1. **Elimination of Silent Guessing:**
   * Ambiguous date or non-standard document formats now safely yield `UNKNOWN` and set `review_required = True`.
2. **Explicit Evidentiary Conflict Tracking:**
   * When visual text and MRZ lines disagree (e.g. Visual DOB `1985-04-12` vs MRZ DOB `1986-04-12`), the system generates a structured `CrossFieldConflict` object with `status: "CONFLICT"`, `resolution_recommendation: "REVIEW_REQUIRED"`.
3. **Traceable Disambiguation Audit Logs:**
   * Character disambiguation ($O \leftrightarrow 0, I \leftrightarrow 1$) on passport numbers records exact index, original character, replacement character, and rule reason into `corrections` list.

---

## 3. Remaining Limitations

* Complex cursive script signatures on identity cards remain unparsed (correctly skipped as non-field visual security features).
* Highly skewed non-standard regional municipal permits require custom bounding box layout annotations.
