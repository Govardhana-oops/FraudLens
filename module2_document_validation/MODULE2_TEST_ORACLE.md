# AI-DIDSS Module 2: Comprehensive Test Oracle Reference

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Total Test Count:** **161 Automated Tests**  
**Date:** 2026-09-03  

---

## 1. Test Suite Architecture & Distribution

| Test Suite File | Test Count | Target Scope & Invariants Verified |
| :--- | :---: | :--- |
| **`tests/test_rule_engine.py`** | 44 | End-to-end evaluation across all 44 standard synthetic document fixtures. |
| **`tests/test_semantic_status_model.py`** | 13 | Core semantic status hierarchy and precedence invariants. |
| **`tests/test_normalizer.py`** | 8 | Date delimiters, character confusion repair, whitespace compaction, Unicode NFKC. |
| **`tests/test_document_type_ambiguity.py`**| 4 | Low classification confidence, universal rule fallback, unknown doc types. |
| **`tests/test_mrz_expanded_standards.py`**| 3 | TD1, TD2, TD3, MRV-A, MRV-B line length and modulo-10 check digits. |
| **`tests/test_property_fuzz.py`** | 30 | Random schema fuzzing, score bounds $[0.0, 1.0]$, determinism ($F(x) = F(x)$). |
| **`tests/test_security_robustness.py`** | 10 | Injection strings, oversized buffers, path traversal, zero fraud label checks. |
| **`tests/test_performance.py`** | 1 | Latency and throughput benchmark verification (< 20 ms). |
| **`tests/test_cross_field_matrix.py`** | 8 | Visual vs MRZ field agreement and chronology cross-matrices. |
| **`tests/test_edge_cases.py`** | 14 | Leap day validation, month/day bounds, Unicode names, null fields. |
| **`tests/test_mrz_validator.py`** | 6 | Standard TD1/TD3 modulo-10 recalculations. |
| **`tests/test_date_validator.py`** | 5 | ISO 8601 syntax and expiration boundary dates. |
| **`tests/test_input_validation.py`** | 5 | Dict, JSON string, malformed JSON, unsupported input types. |
| **`tests/test_document_validators.py`** | 4 | Mandatory field presence, driver age threshold, permit categories. |
| **`tests/test_consistency_validator.py`**| 3 | Visual vs MRZ conflict propagation. |
| **`tests/test_uncertainty_handling.py`** | 3 | Module 1 OCR uncertainty propagation. |
| **Total Test Suite Size** | **161** | **100% Passing (0 failures, 0 skips)** |
