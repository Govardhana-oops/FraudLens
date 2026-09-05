# Stage 6: Reproducibility & Benchmark Environment Specification

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Timestamp:** 2026-09-02  

---

## 1. System & Hardware Environment

* **Operating System:** Microsoft Windows 10 Home (64-bit, Build 19045)
* **Processor (CPU):** AMD Ryzen 3 3250U with Radeon Graphics (2 Cores, 4 Logical Processors, 2.60 GHz base)
* **System RAM:** 8.00 GB (7.67 GB Usable)
* **GPU / Accelerator:** Integrated AMD Radeon Vega 3 (CPU multi-threaded execution utilized for all pipelines)

---

## 2. Software & Python Environment

* **Python Runtime:** Python 3.13.14 (64-bit)
* **Key Dependencies:**
  * `opencv-python==5.0.0.93` (Core computer vision, homography, CLAHE, Hough line transform)
  * `numpy==2.5.2` (Vectorized array math and calibration metrics)
  * `pillow==12.3.0` (Image I/O and spatial bounding)
  * `pyyaml==6.0.3` (Configuration parsing)
  * `pytest==9.1.1` (Automated test suite)

---

## 3. Dataset Configuration & Versioning

* **Synthetic Benchmark Dataset:** `SynthID-Doc v1.0`
* **Cleaned Dataset Total:** 240 document images across 120 unique document identities.
* **Train Partition:** `data/train/` (168 images across 84 document identities).
* **Validation Partition:** `data/validation/` (36 images across 18 document identities).
* **Internal Test Partition:** `data/test/` (36 images across 18 document identities).
* **External Test Partition:** `data/external_test/` (30 images across 15 document identities) — **100% UNTOUCHED (Quarantined for Stage 7)**.

---

## 4. Exact Execution & Reproduction Commands

```powershell
# 1. Run Complete Unit & Integration Test Suite (26/26 Passing)
pytest tests/ -v -p no:cacheprovider

# 2. Run Comprehensive Stage 6 Benchmark Evaluation
python scripts/evaluate_final_ocr.py

# 3. Run Production Field Extraction CLI on an image
python scripts/extract_fields.py --input data/cleaned/DOC_PASSPORT_0001_v1.png --output outputs/extraction_results/
```
