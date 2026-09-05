# AI-DIDSS Module 2: Status Resolution Specification & Semantic Model

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**Version:** `v0.2.1-SEMANTIC-CORRECTION`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-02  

---

## 1. Core Semantic Taxonomy

Module 2 makes an explicit, rigorous distinction between **missing/unextracted data** (OCR uncertainty) and **demonstrably invalid data** (substantive rule violation).

### A. Unavailable / Unreliably Extracted Field (OCR Uncertainty)
* **Definition:** A required field is absent from Module 1's output, populated with `None`, or marked `status: "UNKNOWN"` by the OCR layer.
* **Interpretation:** The optical capture may have been blurry, occluded, or unread by OCR. Absence of evidence is NOT evidence of fraud or physical invalidity.
* **Rule Check Status:** `UNKNOWN`.
* **Deterministic Outcome:** **`UNKNOWN`** (if primary document identifier is missing) or **`REVIEW_REQUIRED`** (if secondary required field is unavailable).
* **Guaranteed Invariant:** An unavailable field **NEVER produces `INVALID`**.

### B. Demonstrably Malformed / Impossible Field (Substantive Failure)
* **Definition:** A required field is extracted and present, but its value violates fundamental calendar mathematics, physical chronology, syntax rules, or cryptographic/modulo check digits.
* **Examples:**
  * Date present as `1985-02-30` (impossible calendar date).
  * Date present as `2001-02-29` (impossible non-leap day).
  * Issue Date `2030-01-01` > Expiry Date `2025-01-01` (inverted chronology).
  * Date of Birth in the future (`2035-01-01`).
  * Passport number `123` (violates alphanumeric syntax length).
  * MRZ Check digit mathematically wrong (Calculated: 9, Found: 0).
  * Bearer age at driver license issuance is 12 years (underage driving violation).
* **Rule Check Status:** `FAIL` (`CRITICAL` severity).
* **Deterministic Outcome:** **`INVALID`**.

### C. Conflicting Evidence (Cross-Field Discrepancy)
* **Definition:** Two zones within the same document offer contradicting readings (e.g. Visual Inspection Zone vs Machine Readable Zone).
* **Examples:**
  * Visual Passport Number `P99999999` != MRZ Number `P12345678`.
  * Visual Date of Birth `1986-04-12` != MRZ Date of Birth `1985-04-12`.
* **Rule Check Status:** `FAIL` (`HIGH` severity).
* **Deterministic Outcome:** **`REVIEW_REQUIRED`** (routes to human officer for adjudication).

### D. Expiration (Temporal State)
* **Definition:** The document is structurally valid and authentic in syntax, but its expiration date strictly precedes the reference verification date (`2026-09-02`).
* **Deterministic Outcome:** **`EXPIRED`**.
* **Precedence Rule:** If a document is expired BUT also has a demonstrably impossible calendar date or chronology (e.g. Issue > Expiry), `INVALID` takes strict precedence over `EXPIRED`.

### E. Unsupported Document Type
* **Definition:** The document category is validly structured in an external domain (e.g. voter card), but outside the screening system's 5 supported identity classes.
* **Deterministic Outcome:** **`UNSUPPORTED_DOCUMENT`**.

### F. Malformed / Empty Input
* **Definition:** Upstream payload decode failure, corrupted image stream, or 0-byte buffer.
* **Deterministic Outcome:** **`INVALID_INPUT`**.

---

## 2. Deterministic Precedence Hierarchy

```
[1. Upstream Input Decode / Payload Failure] ─────► INVALID_INPUT
                   │ (Pass)
                   ▼
[2. Unsupported Document Class] ──────────────────► UNSUPPORTED_DOCUMENT
                   │ (Pass)
                   ▼
[3. Missing Primary ID / Unidentifiable Doc] ─────► UNKNOWN
                   │ (Pass)
                   ▼
[4. Demonstrably Malformed / Impossible Data] ────► INVALID
   ├── Impossible calendar date (Feb 30)
   ├── Issue date after expiration
   ├── DOB in future or after issue
   ├── Present but invalid identifier syntax
   ├── ICAO Modulo-10 checksum failure
   └── Underage driver license issuance (< 16 yrs)
                   │ (Pass)
                   ▼
[5. Chronologically Past Expiration] ─────────────► EXPIRED
                   │ (Pass)
                   ▼
[6. Discrepancies & Optical Uncertainty] ─────────► REVIEW_REQUIRED
   ├── Visual vs MRZ field conflicts
   ├── Secondary field unavailable
   └── Module 1 review_required flag
                   │ (Pass)
                   ▼
[7. All Rules Passed Cleanly] ────────────────────► VALID
```

---

## 3. Validation Score Formula & Semantics

$$\text{Validation Score} = \frac{\sum_{i \in \text{Passed Rules}} w_i + 0.8 \sum_{j \in \text{Warnings}} w_j}{\sum_{k \in \text{Applicable Rules (PASS/FAIL/WARNING)}} w_k} \in [0.0, 1.0]$$

### Exact Score Rules:
1. **Exclusion of Uncertainty:** Rules evaluated as `UNKNOWN`, `SKIPPED`, or `NOT_APPLICABLE` are strictly excluded from the denominator.
2. **Neutral Score for Unknown Documents:** Unidentifiable documents or missing primary ID payloads produce a neutral score of `0.50`.
3. **Cap:** Score cannot exceed `1.0` and cannot fall below `0.0`.
4. **Non-Equivalence:** The score is **strictly an optical data consistency index**. It is NOT a fraud probability, legal authenticity score, or border detention recommendation.
