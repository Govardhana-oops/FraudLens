# AI-DIDSS Module 2: Upstream Module 1 Uncertainty Handling Specification

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-02  

---

## 1. Upstream Module 1 Reality & Uncertainty Profile

During Stage 7 testing and Stage 8 manual verification of Module 1, several empirical behaviors were documented:
1. **Multi-Class Affinity:** Travel Visas and National IDs carrying MRZs are frequently classified as `passport` by Module 1.
2. **Conservative Layout Fallback:** Unanchored driver's licenses often produce `status: "UNKNOWN"` or `document_type: "unknown_document"`.
3. **High Review Routing:** Low-contrast or noisy captures produce an $83.33\%$ `review_required: true` flag to prevent false claims.
4. **Omission over Hallucination:** Unreadable visual lines are omitted from extraction rather than guessed.

---

## 2. Module 2 Uncertainty Propagation Principles

### Principle 1: No Penalization of Omissions as Formatting Errors
If a field was not extracted by Module 1 (or has `status: "UNKNOWN"`), Module 2 records the format check as `UNKNOWN` or `FIELD_NOT_EXTRACTED` rather than failing it as an invalid alphanumeric string.

### Principle 2: Soft Constraint Evaluation on Ambiguous Document Types
If Module 1 classifies a visa as a `passport` with borderline confidence ($\approx 0.50$):
* Module 2 executes universal checks (date validity, expiration, MRZ checksums).
* If MRV-specific structures are detected, Module 2 evaluates visa constraints and does not fail mandatory passport booklet rules that are not applicable to visa stickers.

### Principle 3: Preservation of Upstream Review Flags
If Module 1 sets `review_required: true` due to optical blur or low OCR confidence:
* Module 2 executes all deterministic rules on the available fields.
* Module 2 **preserves the `review_required: true` flag** in its final output to ensure human officer adjudication.

### Principle 4: Graceful Handling of Empty OCR Buffers
When OCR returns an empty text buffer (e.g. in environments without a local Tesseract binary on Windows PATH), Module 1 outputs `status: "UNKNOWN"`. Module 2 safely transforms this into `overall_status: "UNKNOWN"`, avoiding fatal crashes or spurious error logs.
