# AI-DIDSS Module 2: Document Validation Architecture Specification

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Version:** `v0.1.0-FOUNDATION`  
**Date:** 2026-09-02  

---

## 1. Module Purpose & Core Scope

Module 2 is an independent, deterministic document verification and evidence evaluation engine. It consumes the structured JSON output emitted by Module 1 OCR and evaluates whether the extracted data is:
* **Structurally Valid:** Complies with documented document layouts and mandatory field schemas.
* **Syntactically Valid:** Adheres to established alphanumeric regex patterns, length constraints, and ISO standards (e.g., ISO 3166-1 alpha-3 country codes, ISO 8601 date formats).
* **Chronologically Valid:** Satisfies temporal constraints ($\text{Date of Birth} < \text{Issue Date} \le \text{Expiry Date}$) and expiration bounds relative to current verification time.
* **Logically & Internally Consistent:** Exhibits agreement across multiple representations of the same data (Visual Inspection Zone vs Machine Readable Zone).
* **Compliant with Official Specifications:** Matches ICAO Doc 9303 (passports/visas/IDs), AAMVA (driver's licenses), and international residence permit specifications.

### The Zero Autonomous Fraud Rule
> [!IMPORTANT]
> **Module 2 is an evidence and validation engine, NOT a judicial fraud determination system.**  
> A validation failure (such as an expired document or a missing optional field) constitutes structured evidence for human officer review. Module 2 **NEVER outputs `FRAUD`, `CRIMINAL`, `DETAIN`, or `REJECT`** as autonomous conclusions.

---

## 2. System Inputs & Outputs

### Input Contract
Module 2 ingests the standardized JSON payload defined in `module1_ocr/MODULE2_INTEGRATION_CONTRACT.md`:
* `status`: Top-level status from Module 1 (`SUCCESS`, `PARTIAL`, `UNKNOWN`, `REVIEW_REQUIRED`, `INVALID_INPUT`, etc.).
* `document_type`: Inferred document category (`value`, `confidence`).
* `fields`: Extracted field dictionary with `value`, `raw_value`, `confidence`, `status`, `warnings`, `corrections`.
* `mrz`: Parsed MRZ structure (`status`, `mrz_format`, `lines`, `checksum_valid`, `checks`).
* `consistency`: Evidentiary cross-field conflict objects.
* `processing_metadata`: Traceability records from upstream vision processing.

### Output Contract
Module 2 produces an explainable, structured validation report:
* `module`: `"module2_document_validation"`
* `module_version`: `"0.1.0"`
* `document_type`: Resolved document category.
* `overall_status`: Controlled enum (`VALID`, `INVALID`, `EXPIRED`, `UNKNOWN`, `REVIEW_REQUIRED`, `INVALID_INPUT`, `UNSUPPORTED_DOCUMENT`, `PROCESSING_ERROR`).
* `validation_score`: Deterministic float $[0.0, 1.0]$ representing rule compliance ratio.
* `checks`: Detailed list of individual validation rule outcomes with `rule_id`, `category`, `status`, `severity`, `message`.
* `field_results`: Granular per-field validation status records.
* `cross_field_conflicts`: Evaluated data discrepancies between MRZ and visual zones.
* `mrz_validation`: Modulo-10 checksum validation findings.
* `warnings`: Informational notices (e.g., upcoming expiration, non-critical field omissions).
* `errors`: Critical validation violations (e.g., impossible calendar date, failed ICAO composite checksum).
* `review_required`: Boolean flag routing ambiguous evidence to secondary human inspection.

---

## 3. End-to-End Validation Pipeline

```
Module 1 Structured JSON Output
              │
              ▼
[1. Input Schema Validation] ────────► (Reject malformed payload -> INVALID_INPUT)
              │
              ▼
[2. Document Type Resolution] ───────► (Uncertain/Unknown -> UNKNOWN / REVIEW_REQUIRED)
              │
              ▼
[3. Field Presence & Completeness] ──► (Required vs Optional vs Conditional)
              │
              ▼
[4. Field Format & Syntax Rules] ────► (Regex, Length, ISO 3166-1 alpha-3)
              │
              ▼
[5. Calendar & Date Validation] ─────► (ISO 8601 YYYY-MM-DD, Leap Year, Future Bounds)
              │
              ▼
[6. Temporal Chronology Rules] ──────► (DOB < Issue <= Expiry, Current Expiration)
              │
              ▼
[7. ICAO Modulo-10 MRZ Verification] ─► (Recalculate [7,3,1] Weights for TD1/TD2/TD3/MRV)
              │
              ▼
[8. Visual vs MRZ Consistency] ──────► (Name, Doc Number, DOB, Expiry, Nationality)
              │
              ▼
[9. Document-Specific Domain Rules] ─► (Passport, Visa, Driver's License, ID, Permit)
              │
              ▼
[10. Rule Aggregation & Scoring] ────► (Deterministic Weighting, Zero False Fraud)
              │
              ▼
Standardized Module 2 Structured Output
```

---

## 4. Supported Document Categories & Specifications

1. **Passports (`passport`):**
   * Format: ICAO Doc 9303 Part 4 (TD3).
   * Rules: 2-line MRZ ($2 \times 44$ chars), Modulo-10 check digits ($[7, 3, 1]$ algorithm), ISO 3166-1 alpha-3 country codes, validity span $\le 10$ years.
2. **Travel Visas (`visa`):**
   * Format: ICAO Doc 9303 Part 7 (MRV-A / MRV-B).
   * Rules: Visa category/type, validity window, stay duration bounds ($\le$ validity window), 2-line MRV check digits.
3. **Driver's Licenses (`driver_license`):**
   * Format: AAMVA International DL/ID Specification.
   * Rules: State/jurisdiction code, alphanumeric license number syntax, minimum driving age ($\ge 16$ years), validity duration $\le 10$ years, vehicle class codes (`A`, `B`, `C`, `D`, `M`).
4. **National Identity Cards (`national_id`):**
   * Format: ICAO Doc 9303 Part 5 (TD1).
   * Rules: 3-line MRZ ($3 \times 30$ chars), national identification number structure, Modulo-10 checksums.
5. **Residence / Work Permits (`permit`):**
   * Format: Standard International Residence/Work Permit Specification.
   * Rules: Permit registration code syntax, authorized categories (`WORK AUTHORIZATION`, `PERMANENT RESIDENCE`, `STUDENT VISA`, `BUSINESS`), sponsor identity presence, validity duration $\le 5$ years.
6. **Unknown / Ambiguous Documents (`unknown_document`):**
   * Safe fallback handler: Produces `UNKNOWN` or `REVIEW_REQUIRED` without crashing or forcing invalid document-type constraints.

---

## 5. Validation Rules Architecture

Module 2 employs a modular, object-oriented rule architecture where every check is encapsulated in an independent `ValidationRule` object:

### Rule Categories
* `SCHEMA`: Input integrity, structural presence of fields.
* `FORMAT`: Regex syntax, string length, character set validation.
* `DATE`: ISO 8601 formatting, calendar validity, leap years.
* `CHRONOLOGY`: Temporal sequencing ($\text{DOB} < \text{Issue} \le \text{Expiry}$), expiration state.
* `MRZ`: Modulo-10 checksum recalculation, ICAO line geometry.
* `CONSISTENCY`: Cross-field visual vs MRZ agreement, intra-document harmony.
* `DOMAIN`: Document-specific operational constraints (e.g. driving age, permit category).

### Rule Severity Levels
* `CRITICAL`: Fatal structural or integrity violation (e.g. invalid date of birth, failed composite MRZ checksum). Prevents document from achieving `VALID` status.
* `HIGH`: Significant discrepancy (e.g. visual vs MRZ number conflict, expired document). Flags `REVIEW_REQUIRED`.
* `MEDIUM`: Non-critical formatting anomaly (e.g. missing optional sponsor field on permit).
* `LOW` / `INFO`: Informational observation (e.g. document expiring within 90 days).

---

## 6. Deterministic Validation Scoring Model

The `validation_score` is a deterministic, explainable ratio computed over applicable evaluated rules:

$$\text{Validation Score} = \frac{\sum_{i \in \text{Passed Rules}} w_i}{\sum_{i \in \text{Applicable Rules}} w_i}$$

Where $w_i$ is the rule severity weight:
* `CRITICAL`: Weight = $1.0$
* `HIGH`: Weight = $0.75$
* `MEDIUM`: Weight = $0.50$
* `LOW`: Weight = $0.25$

> [!NOTE]
> The validation score measures **rule compliance**, NOT fraud probability. All failed rules are preserved with explicit human-readable reasons in the output report.

---

## 7. Uncertainty & Review Propagation

Module 2 strictly respects upstream uncertainty from Module 1:
* If Module 1 marks a field as `UNKNOWN`, Module 2 records the field format check as `UNKNOWN` rather than penalizing it as `INVALID`.
* If Module 1 flagged `REVIEW_REQUIRED` due to OCR noise, Module 2 preserves the review flag while executing deterministic checks on all extractable fields.
* If a document is classified as `unknown_document`, Module 2 executes generic date and syntax checks and routes the case as `UNKNOWN` / `REVIEW_REQUIRED`.

---

## 8. Testing Strategy & Isolation

Module 2 is tested in complete isolation from external services, networks, or databases:
1. **Unit Tests:** Direct validation of isolated rule functions (leap years, checksums, regexes).
2. **Component Tests:** Direct execution of document-specific validator classes.
3. **Engine Tests:** End-to-end execution of `RuleEngine` across 11 synthetic test cases (valid, invalid, expired, malformed).
4. **Frozen Module 1 Integration Test:** Direct consumption of actual frozen output produced by `module1_ocr.interface.DocumentOCR`.

---

## 9. Security & Privacy Baseline

* **Zero External Network Dependencies:** Operates 100% offline.
* **Input Sanitization:** Rejects inputs $> 5\text{MB}$ and nested recursive payloads.
* **Zero PII Logging:** Diagnostic logging contains rule IDs and status flags, never raw document names or identifiers.
* **Strict Immutability:** Module 2 treats input dictionaries as read-only.
