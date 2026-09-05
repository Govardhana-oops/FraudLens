# AI-DIDSS Module 2: Visual vs MRZ Consistency Specification

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Overview & Evaluation Scope

Machine Readable Travel Documents (MRTDs) feature two redundant zones:
1. **Visual Inspection Zone (VIZ):** Human-readable text (variable layouts, fonts, and localization).
2. **Machine Readable Zone (MRZ):** Standardized OCR-B font text adhering to ICAO Doc 9303.

Module 2 evaluates cross-zone agreement across 4 primary fields:
* **Document Number:** Booklet / identity number.
* **Nationality:** ISO 3166-1 alpha-3 code.
* **Date of Expiry:** Expiration date.
* **Date of Birth:** Birth date.

---

## 2. Decision Matrix

| Comparison Scenario | Visual Value | MRZ Value | Validation Check Status | Overall Status Impact | Severity |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Exact Character Match** | `"P12345678"` | `"P12345678"` | **`PASS`** | Contributes to `VALID` | `HIGH` |
| **Normalized Equivalence** | `"P 1234 5678"` | `"P12345678"` | **`PASS`** | Contributes to `VALID` (with normalization audit log) | `HIGH` |
| **Substantive Mismatch** | `"P99999999"` | `"P12345678"` | **`FAIL`** | **`REVIEW_REQUIRED`** | `HIGH` |
| **Missing Visual Field** | `None` / `""` | `"P12345678"` | **`UNKNOWN`** | Preserves uncertainty $\rightarrow$ `UNKNOWN` / `REVIEW_REQUIRED` | `HIGH` |
| **Missing MRZ Field** | `"P12345678"` | `None` (Visual-only crop) | **`NOT_APPLICABLE`** | Skipped without penalty for non-MRZ crops | `INFO` |

---

## 3. Mandatory Non-Fraud Invariant

> [!IMPORTANT]
> A discrepancy between Visual text and MRZ text (e.g. optical misread of `O` as `D`) constitutes **evidence for human officer adjudication (`REVIEW_REQUIRED`)**, NOT autonomous proof of physical tampering or forgery. Downstream forensic analysis is performed by Module 3.
