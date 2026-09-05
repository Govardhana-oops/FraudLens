# Stage 7: Dedicated External Test Reproducibility Specification

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Timestamp:** 2026-09-02  

---

## 1. System & Execution Environment

* **Operating System:** Microsoft Windows 10 Home (64-bit, Build 19045)
* **Processor (CPU):** AMD Ryzen 3 3250U with Radeon Graphics (2.60 GHz, 2 Cores, 4 Threads)
* **RAM:** 8.00 GB (7.67 GB Usable)
* **Python Environment:** Python 3.13.14 (64-bit)
* **Dependencies:** `opencv-python==5.0.0.93`, `numpy==2.5.2`, `pillow==12.3.0`, `pyyaml==6.0.3`, `pytest==9.1.1`

---

## 2. Frozen System Checksums

Recorded in [models/frozen_manifest.json](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/module1_ocr/models/frozen_manifest.json):

| Component File | Role | SHA-256 Checksum |
| :--- | :--- | :--- |
| `src/preprocessing/pipeline.py` | Core Vision Preprocessing | `9cb2f643e2fbc4df7e0fe727ba0f0322b62d8544f1c1f547806540c49bc8061d` |
| `src/preprocessing/roi_extractor.py` | Multi-Scale ROI Zoning | `7b66804a919016fb310da5fb7a3e74659b8be434f0c40e107f90fbb6ca45efb0` |
| `src/ocr/mrz_parser.py` | ICAO Doc 9303 MRZ Engine | `f6ff3a27c320a16b97621c0ad1e32d56a2364c20573ae0317e3f42bca0d2cb2f` |
| `src/extraction/pipeline.py` | Document Understanding Pipeline | `1ef9c8112521713b194a20b080f550fe86a117094b8e235cb9aa910c666f7f6f` |
| `src/extraction/validator.py` | Field & Chronology Validator | `a5f4581c3c2b8b981cf3ec55e1c4df29ae7d9d71439281a8b2520dfcb52e6931` |
| `src/extraction/normalizer.py` | ISO Normalizer & Disambiguator | `c8742b66e01a1829e16089bbab94e09fefec1d7e237fb3e75a59a7f34c2ee39a` |

---

## 3. Exact Reproduction Command

```powershell
# Execute the automated external evaluation suite
python scripts/evaluate_external_test.py
```
