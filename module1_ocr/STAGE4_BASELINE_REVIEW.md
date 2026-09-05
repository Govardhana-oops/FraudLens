# Stage 4: OCR Baseline Review & Improvement Diagnostics

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Date:** 2026-09-02  
**Baseline Model:** `DocumentOCR-v1.0-baseline`  

---

## 1. Executive Summary of Baseline Performance

In Stage 3, we evaluated the baseline OCR pipeline across the **Validation Split (36 images, 18 doc groups)** and **Held-out Test Split (36 images, 18 doc groups)**.

### Stage 3 Baseline Metrics:
* **Test Field F1-Score:** `17.59%`
* **Test Exact Match Ratio:** `12.96%`
* **Character Error Rate (CER):** `0.0000` (on successfully identified token characters)
* **Word Error Rate (WER):** `0.0000`
* **Mean Processing Latency:** `60.7ms` on CPU

---

## 2. Identified Weaknesses by Document Type

| Document Type | Baseline F1 | Primary Failure Mechanism |
| :--- | :--- | :--- |
| **Driver's License (AAMVA)** | `0.00%` | Unstructured global OCR text lacked spatial bounding box associations; complex multiline addresses and vehicle class codes failed to match rigid linear regexes. |
| **National ID (TD1)** | `0.00%` | Missing static `"CITIZEN ID"` anchor in variable national card layouts; TD1 3-line MRZ zone was not segmented at high DPI. |
| **Travel Visa (MRV-A)** | `0.00%` | Visa number and validity window tokens collided with bearer biographical lines due to lack of region-of-interest (ROI) isolation. |
| **Passport (ICAO TD3)** | `25.00%` | Global extraction caught MRZ surname/given names, but failed to extract VIZ date fields and issuing country codes reliably without spatial anchoring. |
| **Residence Permit** | `66.67%` | Strongest baseline performer due to distinctive `"HOLDER:"` and `"PERMIT NO:"` headers, but missed employer/sponsor lines when line breaks shifted. |

---

## 3. Most Problematic Fields

1. **Addresses (`address`):** Highly variable formatting across 1 to 3 lines with street, city, postal code, and country abbreviations.
2. **Dates (`date_of_birth`, `issue_date`, `expiry_date`):** Ambiguity between `YYYY-MM-DD`, `DD/MM/YYYY`, and `YYMMDD` without contextual proximity to `"DOB"` / `"EXP"` labels.
3. **Document Numbers (`license_number`, `id_number`, `visa_number`):** Prefixes (`DL-`, `ID-`, `RP-`, `V`) often detached from numerical sequences in unsegmented OCR output.
4. **Biographical Names (`full_name`, `surname`, `given_names`):** Disconnect between single-string VIZ full names and delimiter-separated MRZ names (`SURNAME<<GIVEN<NAMES`).

---

## 4. Most Promising Improvement Opportunities

1. **Document-Type Specific ROI Segmentation:** Decompose documents into designated spatial regions (Header ROI, Photo ROI, VIZ Form ROI, and MRZ/Barcode ROI) before running OCR.
2. **Layout-Aware Spatial Proximity Matching:** Instead of linear string regexes, cluster label-value pairs using normalized bounding box distance ($dx, dy$) and vertical alignment.
3. **Domain Dictionary Normalization:** Integrate ICAO Doc 9303 country dictionaries (ISO 3166-1 alpha-3), AAMVA vehicle class mappings, and standard date format normalizers.
4. **MRZ & VIZ Cross-Field Fusion:** Automatically cross-reference and backfill verified MRZ biographical fields into VIZ attributes when VIZ visual contrast is degraded.
