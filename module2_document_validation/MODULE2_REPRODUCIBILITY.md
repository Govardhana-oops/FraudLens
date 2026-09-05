# AI-DIDSS Module 2: Reproducibility & Independent Verification Guide

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**Release Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Environment & Dependencies

* Python $\ge 3.10$
* Dependencies: `pytest`, `pydantic`, `pyyaml`

---

## 2. Independent Verification Execution

```powershell
# Step 1: Navigate to Module 2 directory
cd c:\Users\guvva\OneDrive\Desktop\PROTOTYPE\module2_document_validation

# Step 2: Run complete 161-test automated suite without cache
pytest tests/ -v -p no:cacheprovider
```

Expected Output:
* **161 passed in ~1.6s (100% pass rate)**
* **0 failed, 0 skipped**

---

## 3. Module 1 Integration Verification

```powershell
# Verify frozen Module 1 OCR remains intact and 100% passing
cd c:\Users\guvva\OneDrive\Desktop\PROTOTYPE\module1_ocr
pytest tests/ -v -p no:cacheprovider
```

Expected Output:
* **34 passed in ~1.8s (100% pass rate)**
