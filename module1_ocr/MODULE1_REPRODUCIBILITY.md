# AI-DIDSS Module 1: Comprehensive Reproducibility Package

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Release Version:** `v1.0.0-FROZEN`  
**Model Version:** `LayoutAware-MultiScale-OCR-v2.0`  
**Date:** 2026-09-02  

---

## 1. Environment & Hardware Specification

* **Operating System:** Windows 10 Home (64-bit, Build 19045) / Linux x86_64 compatible
* **Processor (CPU):** AMD Ryzen 3 3250U with Radeon Graphics (2.60 GHz, 2 Cores, 4 Threads)
* **Memory (RAM):** 8.00 GB (7.67 GB Usable)
* **Python Runtime:** Python 3.13.14 (64-bit)

---

## 2. Dependency Manifest

```
fastapi>=0.110.0
uvicorn>=0.28.0
httpx>=0.27.0
python-multipart>=0.0.9
opencv-python>=4.8.0
numpy>=1.24.0
pillow>=10.0.0
pydantic>=2.5.0
pyyaml>=6.0.1
pytest>=7.4.0
```

Install via:
```powershell
pip install -r requirements.txt
pip install fastapi uvicorn httpx python-multipart
```

---

## 3. Cryptographic Component Manifest

Recorded in [models/frozen_manifest.json](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/module1_ocr/models/frozen_manifest.json):

| File Path | Role | SHA-256 Hash |
| :--- | :--- | :--- |
| `src/interface.py` | Public Interface & API Boundary | `8ebf63f538cb33246ebcfd9d28dbd60dbfb5a73e6d18a383d47bf1451b66fe6e` |
| `src/preprocessing/pipeline.py` | Vision Preprocessing | `9cb2f643e2fbc4df7e0fe727ba0f0322b62d8544f1c1f547806540c49bc8061d` |
| `src/preprocessing/roi_extractor.py` | Multi-Scale ROI Zoning | `7b66804a919016fb310da5fb7a3e74659b8be434f0c40e107f90fbb6ca45efb0` |
| `src/ocr/mrz_parser.py` | ICAO Doc 9303 MRZ Engine | `f6ff3a27c320a16b97621c0ad1e32d56a2364c20573ae0317e3f42bca0d2cb2f` |
| `src/extraction/pipeline.py` | Document Understanding Pipeline | `1ef9c8112521713b194a20b080f550fe86a117094b8e235cb9aa910c666f7f6f` |
| `src/extraction/validator.py` | Field & Chronology Validator | `a5f4581c3c2b8b981cf3ec55e1c4df29ae7d9d71439281a8b2520dfcb52e6931` |
| `src/extraction/normalizer.py` | ISO Normalizer & Disambiguator | `c8742b66e01a1829e16089bbab94e09fefec1d7e237fb3e75a59a7f34c2ee39a` |

---

## 4. Execution Commands

### A. Run Test Suite (All 34 Unit & Integration Tests)
```powershell
pytest tests/ -v -p no:cacheprovider
```

### B. Start FastAPI REST Service
```powershell
uvicorn src.api:app --host 0.0.0.0 --port 8000
# Or via package CLI
python -m src --server --port 8000
```

### C. Execute CLI Extraction
```powershell
python scripts/ocr_cli.py --input data/cleaned/DOC_PASSPORT_0001_v1.png --output outputs/result.json
```

### D. Run Dedicated External Benchmark
```powershell
python scripts/evaluate_external_test.py
```
