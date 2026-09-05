# AI-DIDSS Module 1: Comprehensive Dataset Quality & Split Report

**Module:** Module 1 (OCR Extraction & Document Data Understanding)  
**Report Generation Timestamp:** 2026-09-02 18:48:36  
**Compliance Standard:** ISO/IEC 19794, ICAO Doc 9303, AAMVA DL Specifications  

---

## 1. Dataset Summary & Inventory

* **Total Raw Files Scanned:** 243
* **Total Valid Cleaned Samples:** 240
* **Total Rejected / Corrupted Files:** 3
* **Total Unique Document Identities:** 120
* **External Test Isolated Samples:** 30 independent identities

### Document Type Breakdown (Raw Scan)
| Document Type | Sample Count |
| :--- | :--- |
| `NO_ANNOTATION` | 2 |
| `driver_license` | 48 |
| `national_id` | 48 |
| `passport` | 48 |
| `permit` | 48 |
| `visa` | 48 |

---

## 2. Data Cleaning & Integrity Audit

The automated cleaning pipeline (`scripts/clean_dataset.py`) evaluated raw document captures across strict dimensional, format, and annotation standards.

### Cleaning Results:
* **Total Evaluated:** 243
* **Total Accepted:** 240
* **Total Rejected:** 3

### Rejection Audit Log:
- ❌ **`DOC_CORRUPTED_HEADER.png`**: Image format error / unreadable: cannot identify image file 'C:\\Users\\guvva\\OneDrive\\Desktop\\PROTOTYPE\\module1_ocr\\data\\raw\\DOC_CORRUPTED_HEADER.png' (File Size: 29 bytes)
- ❌ **`DOC_CORRUPTED_ZERO_BYTE.png`**: Corrupted: Zero-byte file (File Size: 0 bytes)
- ❌ **`DOC_REJECTED_TINY_DIMENSIONS.png`**: Dimension violation: 50x50 is below minimum 200x200 (File Size: 87 bytes)

---

## 3. Annotation Schema & Geometry Validation

The annotation validator (`scripts/validate_annotations.py`) verified bounding box coordinates ($[x_{min}, y_{min}, x_{max}, y_{max}]$ within image bounds), non-empty ground truth strings, and required field completeness per ICAO/AAMVA specifications.

* **Cleaned Annotations Tested:** 240 records
* **External Annotations Tested:** 30 records
* **Total Violations / Schema Inversions:** 0
* **Validation Outcome:** **PASS**

---

## 4. Dataset Partitioning & Data Leakage Certification

To guarantee **Zero Data Leakage**, the dataset was partitioned strictly by **Document Identity Group (`document_id`)**, ensuring that multiple capture conditions or variations of the same document never appear across different splits.

| Partition | Document Groups (% of Total) | Total Images | Document Type Breakdown |
| :--- | :--- | :--- | :--- |
| **Train** | 84 groups (70.0%) | 168 images | national_id: 36, passport: 36, permit: 32, driver_license: 34, visa: 30 |
| **Validation** | 18 groups (15.0%) | 36 images | national_id: 6, permit: 8, visa: 12, passport: 8, driver_license: 2 |
| **Test** | 18 groups (15.0%) | 36 images | driver_license: 12, permit: 8, visa: 6, passport: 4, national_id: 6 |
| **External Test (Isolated)** | 30 independent identities | 30 images | Passports, Visas, Driver's Licenses, National IDs, Permits |

### Mathematical Leakage Proof:
* $\text{Train Group IDs} \cap \text{Validation Group IDs} = \emptyset$ (0 overlapping IDs)
* $\text{Train Group IDs} \cap \text{Test Group IDs} = \emptyset$ (0 overlapping IDs)
* $\text{Validation Group IDs} \cap \text{Test Group IDs} = \emptyset$ (0 overlapping IDs)
* $\text{External Test IDs} \cap \text{Train/Val/Test IDs} = \emptyset$ (0 overlapping IDs)
* **Certification Status:** **`ZERO_LEAKAGE_CERTIFIED`**

---

## 5. Dataset Balance & Quality Attributes

* **Document Types:** Balanced across 5 core document categories (Passport, Visa, Driver's License, National ID, Residence Permit).
* **Optical Variations:** Standard flatbed clean scans, non-uniform lighting / shadow gradients, mild lens blur, and sensor noise captures.
* **Ground Truth Completeness:** 100% of accepted samples contain exact character-level text, MRZ checksums, and normalized visual zone bounding boxes.

---

## 6. Dataset Limitations & Future Augmentation Vectors

1. **Synthetic Guilloche & Hologram Complexity:** While the current dataset provides exact ICAO MRZ and AAMVA layout geometry, physical optical security features (OVDs, iridescent ink, holographic overlays) require supplementary real-world benchmark cross-validation (e.g., MIDV-500/2019).
2. **Language Coverage:** Current synthetic dictionary focuses on Latin alphanumeric scripts; Arabic, Cyrillic, and Asian scripts should be incorporated for international visa processing.
3. **Capture Diversity:** Stage 3 Preprocessing will introduce on-the-fly random perspective skew, specular glare synthesis, and chromatic aberration to stress-test OCR robustness.

---

## 7. Stage 2 Readiness Certification

* **Data Cleaning:** **PASSED** (100% of corrupted/invalid edge cases detected and segregated).
* **Annotation Schema:** **PASSED** (0 geometry violations, 100% schema completeness).
* **Data Leakage:** **CERTIFIED ZERO LEAKAGE** (Strict document-level partitioning).
* **External Test Isolation:** **CERTIFIED ISOLATED** (30 independent out-of-distribution identities reserved).

**The Module 1 dataset is verified, clean, structured, and READY for Stage 3 (OCR Preprocessing & Baseline Development).**
