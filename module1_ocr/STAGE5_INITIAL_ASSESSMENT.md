# Stage 5: Initial Implementation Assessment & Engineering Plan

**Module:** Module 1 (OCR Extraction & Document Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-02  
**Current Active Model:** `LayoutAware-MultiScale-OCR-v2.0`  
**Baseline Model:** `DocumentOCR-v1.0-baseline`  

---

## 1. Assessment of Current Implementation

### What is Already Functional:
1. **Preprocessing Pipeline (`src/preprocessing/`):**
   * `quality_check.py`: Laplacian blur detection ($\sigma^2$), glare ratio calculation, resolution verification.
   * `crop.py`: 4-point perspective contour homography.
   * `deskew.py`: Hough transform median angle deskewing.
   * `illumination.py`: LAB CLAHE illumination normalization.
   * `roi_extractor.py`: Multi-scale document zone segmenter (Header, VIZ, MRZ with 1.5x upscaling, Photo).
2. **OCR Engine & MRZ Parser (`src/ocr/`):**
   * `engine.py`: Multi-backend OCR engine abstraction.
   * `mrz_parser.py`: ICAO Doc 9303 modulo-10 check digit math on TD1, TD2, TD3, and MRV-A/B formats with robust string padding.
3. **Extraction & Schemas (`src/extraction/`):**
   * `schema.py`: Basic dataclass schema (`ExtractedField`, `MRZValidationResult`, `DocumentExtractionResult`).
   * `layout_extractor.py`: Layout-aware field extractor with preliminary date normalization and MRZ-to-VIZ backfilling.
4. **Unit Test Suite (`tests/`):**
   * 17 unit tests passing across preprocessing, MRZ checksums, extraction, and evaluation metrics.

### Identified Deficiencies & Fragilities:
1. **Schema Expressiveness:**
   * Current `ExtractedField` lacks tracking of `raw_value`, `extraction_method` (e.g., `mrz_direct`, `spatial_proximity`, `pattern_regex`), `source` (`visual_text` vs `mrz` vs `barcode`), `validation_status`, `warnings`, and `corrections_applied`.
2. **Document Classification:**
   * Document type detection relies primarily on raw text substring presence without confidence scoring or geometric aspect ratio checks.
3. **Field Normalization & Disambiguation:**
   * Normalization is currently ad-hoc inside extraction rather than managed by a dedicated, reversible normalizer with traceable correction logs (e.g., field-specific $O \leftrightarrow 0, I \leftrightarrow 1, S \leftrightarrow 5$ disambiguation).
4. **Cross-Field Consistency & Conflict Representation:**
   * When visual text and MRZ conflict (e.g. Visual DOB vs MRZ DOB), the system lacks an explicit `CONFLICT` object detailing visual vs MRZ values, which is essential for downstream Module 2 and Module 5 processing.
5. **Validation Engine:**
   * Lacks a dedicated `FieldValidator` verifying chronological date logic ($\text{DOB} < \text{Issue} < \text{Expiry}$), ISO 3166-1 alpha-3 membership, and structural format masks.

---

## 2. Supported Document Types & Target Field Matrix

| Document Type | Supported Core Fields | Primary Extraction Methods |
| :--- | :--- | :--- |
| **Passport (ICAO TD3)** | `full_name`, `surname`, `given_names`, `passport_number`, `nationality`, `issuing_country`, `date_of_birth`, `date_of_expiry`, `gender`, `date_of_issue`, `mrz_line1`, `mrz_line2` | High-DPI TD3 MRZ parser + VIZ spatial label-value matcher + Bidirectional cross-validation |
| **Travel Visa (MRV-A)** | `visa_number`, `full_name`, `surname`, `given_names`, `passport_number`, `nationality`, `date_of_birth`, `issue_date`, `expiry_date`, `entries`, `mrz_line1`, `mrz_line2` | MRV-A MRZ parser + VIZ validity window label-value matcher |
| **Driver's License (AAMVA)** | `license_number`, `full_name`, `address`, `date_of_birth`, `issue_date`, `expiry_date`, `vehicle_class`, `gender` | Multiline VIZ spatial proximity clustering + AAMVA keyword layout anchors |
| **National ID (TD1)** | `id_number`, `full_name`, `surname`, `given_names`, `nationality`, `date_of_birth`, `expiry_date`, `gender`, `mrz_line1`, `mrz_line2`, `mrz_line3` | TD1 3-line MRZ parser + VIZ header anchor matcher |
| **Residence Permit** | `permit_number`, `full_name`, `permit_category`, `valid_until`, `sponsor` | Spatial block extractor + Employer/Sponsor line-boundary parser |

---

## 3. Stage 5 Engineering & Implementation Plan

1. **Step 1: Standardized Schema Expansion (`src/extraction/schema.py` & `FIELD_SCHEMA.md`):**
   * Expand `ExtractedField` to include `raw_value`, `source`, `confidence`, `extraction_method`, `validation_status` (`VALID`, `INVALID`, `UNKNOWN`, `NOT_APPLICABLE`), `warnings`, and `corrections`.
   * Add `CrossFieldConflict` schema for explicit visual vs MRZ mismatch recording.
2. **Step 2: Conservative Document Type Classifier (`src/extraction/doc_classifier.py`):**
   * Multi-signal scoring (Header text + MRZ format + Layout structure) returning `document_type` and `document_type_confidence`. Fallback to `UNKNOWN` if below threshold.
3. **Step 3: Controlled Normalizer & Traceable Correction Engine (`src/extraction/normalizer.py`):**
   * ISO 8601 date normalizer (`YYYY-MM-DD`), whitespace compressor, pattern-specific character disambiguator with detailed audit logs.
4. **Step 4: Field Validation & Cross-Field Consistency Engine (`src/extraction/validator.py`):**
   * Implement chronological date validation ($\text{DOB} < \text{Issue} < \text{Expiry}$), ISO country codes, and explicit visual vs MRZ consistency checks.
5. **Step 5: Unified Production Field Extraction Pipeline (`src/extraction/pipeline.py` & CLI `scripts/extract_fields.py`):**
   * End-to-end integration: Preprocessing $\rightarrow$ OCR Tokens $\rightarrow$ Doc Classification $\rightarrow$ Multi-Scale ROI $\rightarrow$ Layout Label-Value Association $\rightarrow$ Normalization $\rightarrow$ Validation $\rightarrow$ Structured Output.
6. **Step 6: Evaluation & Testing:**
   * Benchmark per-field Precision, Recall, F1, Exact Match on Validation and Test splits.
   * Expand test suite in `tests/` covering normal, difficult, and safety/robustness cases.
