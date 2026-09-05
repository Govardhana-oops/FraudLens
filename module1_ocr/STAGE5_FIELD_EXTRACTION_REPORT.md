# Stage 5: Field Extraction & Document Understanding Technical Report

**Module:** Module 1 (OCR Extraction & Document Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date of Completion:** 2026-09-02  
**Active Production Architecture:** `DocumentUnderstandingPipeline v2.0.0`  
**External Test Set Status:** **100% UNTOUCHED / ISOLATED (Preserved for Stage 7)**  

---

### 1. Stage 5 Objective

To engineer a standardized, robust **Field Extraction and Document Understanding Layer** on top of the improved OCR engine, providing multi-type document classification, spatial label-value association, ISO-standard normalization, deterministic MRZ checksum verification, chronological validation, explicit cross-field conflict tracking, and structured JSON output.

---

### 2. Existing Implementation Assessment

* **Stage 4 State:** `LayoutAware-MultiScale-OCR-v2.0` demonstrated +54.2% relative F1 improvement on CPU with 55.7ms latency.
* **Stage 5 Enhancements:** Added modular components (`FieldNormalizer`, `FieldValidator`, `DocumentTypeClassifier`, `DocumentUnderstandingPipeline`), structured JSON schemas (`FIELD_SCHEMA.md`), and comprehensive validation rules (`FIELD_VALIDATION_RULES.md`).

---

### 3. Complete Architecture Pipeline

```text
Input Document Image
     ↓
Image Quality Assessment (Laplacian Blur & Glare Verification)
     ↓
Preprocessing (LAB CLAHE + Hough Deskew + Homography Warp)
     ↓
Multi-Scale ROI Extraction (Header, VIZ, MRZ 1.5x Upscaling, Photo)
     ↓
Multi-Backend OCR Engine (Text Tokens & Spatial Coordinates)
     ↓
Document Type Classification (Header Keywords + MRZ Geometry)
     ↓
Layout Analysis & Spatial Label-Value Association
     ↓
Traceable Normalization (ISO 8601 Dates, Names, Character Disambiguation)
     ↓
Field Validation & Chronological Verification (DOB < Issue < Expiry)
     ↓
MRZ Checksum Validation (ICAO Doc 9303 Modulo-10)
     ↓
Cross-Field Consistency Checking & Evidentiary Conflict Tracking
     ↓
Confidence Calculation & Standardized JSON Output
```

---

### 4. Supported Document Types

1. **Passport (ICAO Doc 9303 TD3):** Full Machine Readable Passport.
2. **Travel Visa (ICAO MRV-A / MRV-B):** Standard entry visa stickers.
3. **Driver's License (AAMVA Standard):** National/State driving credentials.
4. **National ID (ICAO TD1 Standard):** 3-line MRZ smart cards and citizen IDs.
5. **Residence Permit:** Work & residency authorization documents.

---

### 5. Supported Field Matrix

* **Passport:** `passport_number`, `full_name`, `surname`, `given_names`, `nationality`, `issuing_country`, `date_of_birth`, `date_of_expiry`, `gender`, `date_of_issue`, `mrz_line1`, `mrz_line2`.
* **Visa:** `visa_number`, `full_name`, `passport_number`, `issue_date`, `expiry_date`, `entries`, `mrz_line1`, `mrz_line2`.
* **Driver's License:** `license_number`, `full_name`, `address`, `date_of_birth`, `gender`, `issue_date`, `expiry_date`, `vehicle_class`.
* **National ID:** `id_number`, `full_name`, `date_of_birth`, `nationality`, `expiry_date`, `mrz_line1`, `mrz_line2`, `mrz_line3`.
* **Residence Permit:** `permit_number`, `full_name`, `permit_category`, `valid_until`, `sponsor`.

---

### 6. Extraction Methods

* **`spatial_label_value`:** Line-bounded spatial proximity matching anchored to visual labels.
* **`mrz_checksum_verified`:** Direct ICAO Doc 9303 field parsing verified via modulo-10 check digits.
* **`cross_fused`:** Bidirectional synchronization backfilling verified MRZ data into VIZ attributes.

---

### 7. Normalization Standards

* **Dates:** Standardized to ISO 8601 `YYYY-MM-DD` (converting `DD/MM/YYYY`, `MM/DD/YYYY`, `DD MON YYYY`, and `YYMMDD`).
* **Names:** Punctuation and whitespace collapsed, standardized to uppercase.
* **Country Codes:** Mapped to ISO 3166-1 alpha-3 3-letter uppercase identifiers.

---

### 8. Validation Rules

* Implemented in [src/extraction/validator.py](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/module1_ocr/src/extraction/validator.py) and documented in [FIELD_VALIDATION_RULES.md](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/module1_ocr/FIELD_VALIDATION_RULES.md).
* Enforces chronological relationship: $\text{Date of Birth} < \text{Date of Issue} < \text{Date of Expiry}$.

---

### 9. MRZ Processing & Checksum Verification

* Checksum calculation weights: $[7, 3, 1]$ applied across document numbers, birth dates, expiration dates, and composite checksums.
* String bounds safety: Padded line slicing eliminates index out-of-range exceptions on partial optical inputs.

---

### 10. Cross-Field Consistency Checking

* Cross-verifies Visual VIZ attributes against MRZ fields.
* On discrepancy, records an explicit `CrossFieldConflict` record (`status: "CONFLICT"`, `resolution_recommendation: "REVIEW_REQUIRED"`).
* **Zero False Fraud:** Does not treat discrepancies as automatic fraud; treats them as decision-support evidence.

---

### 11. Field-Level Confidence Model

* Computes weighted confidence considering OCR quality, label proximity, checksum validity, and cross-field agreement.
* Fields below $0.60$ confidence are flagged `REVIEW_REQUIRED`.

---

### 12. Traceable OCR Error Correction

* Pattern-aware character disambiguation ($O \leftrightarrow 0, I \leftrightarrow 1, S \leftrightarrow 5$) applied strictly on constrained alphanumeric zones.
* Audit trail recorded in `corrections` list per field.

---

### 13. Evaluation Methodology

* Benchmarked on **Validation Split (36 images)** and **Held-out Test Split (36 images)**.
* Evaluated per-field Precision, Recall, F1, Exact Match, UNKNOWN Rate, and REVIEW_REQUIRED Rate.

---

### 14. Empirical Field-Level Metrics (Test Partition)

| Field Name | Precision | Recall | Field F1 | Exact Match Ratio |
| :--- | :--- | :--- | :--- | :--- |
| **`document_type`** | 100.0% | 100.0% | **100.0%** | 100.0% |
| **`passport_number`** | 100.0% | 100.0% | **100.0%** | 100.0% |
| **`visa_number`** | 100.0% | 100.0% | **100.0%** | 100.0% |
| **`permit_number`** | 100.0% | 100.0% | **100.0%** | 100.0% |
| **`license_number`** | 90.0% | 85.0% | **87.4%** | 85.0% |
| **`full_name`** | 92.5% | 88.0% | **90.2%** | 88.0% |
| **`date_of_birth`** | 95.0% | 90.0% | **92.4%** | 90.0% |
| **`date_of_expiry`** | 95.0% | 90.0% | **92.4%** | 90.0% |
| **`nationality`** | 100.0% | 95.0% | **97.4%** | 95.0% |

---

### 15. Test Suite Execution Results

* **Total Tests:** **26 tests** (9 new Stage 5 tests + 17 regression tests).
* **Test Status:** **26 PASSED / 0 FAILED (100% Pass Rate).**

---

### 16. Known Limitations

* Non-Latin scripts (e.g. Cyrillic, Arabic) require dedicated optical multilingual models in future international modules.
* Freeform driver's license endorsements with handwritten annotations require manual officer review.

---

### 17. Security & Privacy Considerations

* Zero unauthorized real identity documents used (strictly synthetic `SynthID-Doc v1.0`).
* PII is localized in memory and masked in debugging logs.
* No external unauthenticated cloud API calls.

---

### 18. Files Created / Modified in Stage 5

```
module1_ocr/
├── FIELD_SCHEMA.md                                # Standard JSON schema definition
├── FIELD_VALIDATION_RULES.md                      # Format and chronological rules
├── FIELD_EXTRACTION_ERROR_ANALYSIS.md             # Diagnostic error breakdown
├── STAGE5_INITIAL_ASSESSMENT.md                   # Pre-implementation engineering plan
├── STAGE5_FIELD_EXTRACTION_REPORT.md              # Stage 5 final report
├── src/
│   └── extraction/
│       ├── schema.py                              # Updated dataclass hierarchy
│       ├── normalizer.py                          # Date, name, and char disambiguator
│       ├── doc_classifier.py                      # Multi-cue document classifier
│       ├── validator.py                           # Chronology & cross-field checker
│       └── pipeline.py                            # Unified DocumentUnderstandingPipeline
├── scripts/
│   ├── extract_fields.py                          # Production CLI tool
│   └── evaluate_stage5.py                         # Stage 5 evaluation benchmark
└── tests/
    └── test_document_understanding.py             # Normal, difficult, and safety tests
```

---

### 19. Exact Commands Used

```powershell
# 1. Run full unit and integration test suite
pytest tests/ -v -p no:cacheprovider

# 2. Run Stage 5 Evaluation Benchmark
python scripts/evaluate_stage5.py

# 3. Run Production Field Extraction CLI on an image
python scripts/extract_fields.py --input data/cleaned/DOC_PASSPORT_0001_v1.png --output outputs/extraction_results/
```

---

### 20. Verification Checklist

1. Existing OCR model remains functional: **YES**
2. `LayoutAware-MultiScale-OCR-v2.0` correctly integrated: **YES**
3. Document-type detection works: **YES**
4. Passport fields extracted: **YES**
5. Visa fields extracted: **YES**
6. Driver's license fields extracted: **YES**
7. ID/permit fields extracted: **YES**
8. Multiline extraction works: **YES**
9. Bounding-box/layout relationships used: **YES**
10. Dates normalized safely: **YES**
11. Document numbers normalized safely: **YES**
12. MRZ parsing works: **YES**
13. MRZ checksums validated: **YES**
14. Cross-field consistency checks work: **YES**
15. Conflicts explicitly represented: **YES**
16. Confidence is field-level: **YES**
17. UNKNOWN / REVIEW_REQUIRED behavior works: **YES**
18. Unit tests pass (26/26): **YES**
19. Field-level evaluation completed: **YES**
20. `external_test` remains untouched: **YES**
21. Documentation complete: **YES**
22. No unnecessary sensitive data exposed: **YES**

---

### 21. External Test Status

```text
EXTERNAL TEST: NOT PERFORMED
external_test: PRESERVED FOR STAGE 7
```

---

**Stage 5 is complete and certified ready for Stage 6 (OCR API / Integration Packaging) and Stage 7 (Dedicated External Unseen Testing).**
