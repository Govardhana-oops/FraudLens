# AI-DIDSS Module 2: Stage 3 Implementation Plan
## Robust Validation Pipeline, OCR-Noise Tolerance & Adversarial Testing

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Stage:** Stage 3 — Robust Validation Pipeline  
**Date:** 2026-09-03  

---

## 1. Current Validation Pipeline Review

The existing Module 2 validation pipeline consists of:
* `src/interface.py`: Public API wrapper (`DocumentValidator`) handling dict, JSON string, and payload inputs.
* `src/schemas/input_schema.py`: Pydantic/Dataclass input parser mapping Module 1 OCR outputs.
* `src/schemas/output_schema.py`: Standardized validation report output schema.
* `src/rules/rule_definition.py`: 20-rule canonical catalog with explicit Authority Tiers (`AUTHORITATIVE`, `PROJECT_SYNTHETIC_RULE`, `HEURISTIC`).
* `src/validators/`:
  * `date_validator.py`: ISO 8601 syntax, physical calendar math, chronology constraints.
  * `mrz_validator.py`: ICAO Doc 9303 line geometry and Modulo-10 7-3-1 check digit recalculation (TD1, TD3, MRV-A).
  * `consistency_validator.py`: Cross-field visual vs MRZ consistency verification.
  * `passport_validator.py`, `visa_validator.py`, `license_validator.py`, `national_id_validator.py`, `permit_validator.py`: Document-specific logic.
* `src/engine/rule_engine.py`: Orchestrator enforcing deterministic status precedence and score computation.

---

## 2. Current Rule Engine Behavior

* **Status Precedence:**
  $$\text{INVALID\_INPUT} \succ \text{UNSUPPORTED\_DOCUMENT} \succ \text{UNKNOWN} \succ \text{INVALID} \succ \text{EXPIRED} \succ \text{REVIEW\_REQUIRED} \succ \text{VALID}$$
* **Score Metric:**
  $$\text{Validation Score} = \frac{\sum_{i \in \text{Passed}} w_i + 0.8 \sum_{j \in \text{Warnings}} w_j}{\sum_{k \in \text{Applicable (Pass/Fail/Warning)}} w_k}$$
  (Excludes `UNKNOWN`, `SKIPPED`, and `NOT_APPLICABLE` rules from the denominator).

---

## 3. Current Normalization Behavior

* Minimal ad-hoc string stripping (`.strip()`, `.replace(" ", "")`).
* No formal normalization audit log or reversible tracking.
* No field-specific character confusion disambiguation (e.g. numeric `O` ↔ `0`, `I` ↔ `1`, `S` ↔ `5`, `B` ↔ `8`, `Z` ↔ `2`).

---

## 4. Current Uncertainty Handling

* Conservative propagation: missing primary identifiers route to `UNKNOWN`.
* Secondary field omissions route to `REVIEW_REQUIRED`.
* Upstream `review_required: true` preserved faithfully.
* Validation score represents optical text consistency, not fraud probability.

---

## 5. Current Document-Type Handling

* Low-confidence document classifications currently execute document-specific rules directly if `document_type.value` is populated.
* Weakness: Classification uncertainty (e.g. `confidence < 0.70`) should restrict execution to document-type-agnostic rules and route to `REVIEW_REQUIRED`.

---

## 6. Weaknesses to Address in Stage 3

1. **Lack of Dedicated Normalization Layer:** Raw OCR noise (e.g., date separators `2020.05.12`, trailing commas, or minor whitespace) needs structured, reversible normalization with audit tracking.
2. **Document-Type Ambiguity Sensitivity:** If Module 1 assigns low confidence to `document_type` (e.g. 0.50), the system must not assume certainty.
3. **Field Confidence Sensitivity:** Low-confidence critical fields must route to `REVIEW_REQUIRED` rather than false `INVALID`.
4. **Expanded MRZ Standards Coverage:** TD2 ($2 \times 36$) and MRV-B ($2 \times 36$) checksums must be fully implemented alongside TD1 ($3 \times 30$) and TD3 ($2 \times 44$).
5. **Adversarial & Fuzz Robustness:** Need systematic testing against edge cases, corrupted Unicode, injection payloads, oversized inputs, and property-based score invariants.

---

## 7. Proposed Changes

1. **`src/normalizers/ocr_normalizer.py` [NEW]:**
   * Field-specific, deterministic normalizer.
   * Records: `original_value`, `normalized_value`, `transformations_applied`, `ambiguity_detected`.
   * Date separator standardization (`YYYY.MM.DD`, `YYYY/MM/DD` $\rightarrow$ `YYYY-MM-DD`).
   * Controlled alphanumeric & numeric character confusion mappings with safety guards.
2. **`src/validators/mrz_validator.py` [UPDATE]:**
   * Add full check digit support for TD2 ($2 \times 36$) and MRV-B ($2 \times 36$).
3. **`src/engine/rule_engine.py` [UPDATE]:**
   * Integrate normalization step before validation checks.
   * Add confidence-aware threshold gating (`doc_type_confidence_threshold = 0.70`, `field_confidence_threshold = 0.60`).
   * If document type confidence $< 0.70$, execute only universal rules (dates, MRZ, consistency) and flag `REVIEW_REQUIRED`.
4. **Specifications & Documents [NEW]:**
   * `DOCUMENT_TYPE_AMBIGUITY.md`
   * `VISUAL_MRZ_CONSISTENCY_SPEC.md`
   * `MODULE2_ROBUSTNESS.md`
   * `MODULE2_EDGE_CASES.md`
   * `MODULE2_SECURITY.md`
   * `MODULE2_PERFORMANCE.md`
   * `MODULE2_TEST_ORACLE.md`
   * `MODULE2_STAGE3_REPORT.md`

---

## 8. Tests Required

* Unit tests for `OCRNormalizer` (whitespace, date separators, case, numeric confusion, audit logging).
* Document type ambiguity tests (low confidence, conflicting types).
* Field confidence threshold tests (low vs high confidence).
* Expanded MRZ tests (TD1, TD2, TD3, MRV-A, MRV-B).
* Adversarial synthetic dataset (40+ new fixtures in `data/adversarial_test_cases/`).
* Property-based & Fuzz tests (`tests/test_property_fuzz.py`).
* Security tests (`tests/test_security_robustness.py`: injection strings, oversized buffers, invalid JSON, nulls, path traversals).
* Performance benchmark tests (`tests/test_performance.py`).

---

## 9. Changes Intentionally NOT Made

* We will **NOT** automatically modify or overwrite Module 1's raw OCR artifacts.
* We will **NOT** blindly autocorrect ambiguous names or document numbers.
* We will **NOT** output `FRAUD` or `CRIMINAL` tags.
* We will **NOT** touch Module 1 source code or models.
