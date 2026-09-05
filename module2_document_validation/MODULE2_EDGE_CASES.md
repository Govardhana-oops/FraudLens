# AI-DIDSS Module 2: Edge-Case & Boundary Catalog

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Verified Boundary Cases

| Category | Boundary Condition | Input Pattern | Evaluated Outcome | Rationale |
| :--- | :--- | :--- | :---: | :--- |
| **Calendar Math** | Century Leap Day | `2000-02-29` | **`PASS`** | 2000 is a divisible by 400 leap year. |
| **Calendar Math** | Standard Leap Day | `2024-02-29` | **`PASS`** | 2024 is divisible by 4. |
| **Calendar Math** | Non-Leap Day | `2023-02-29` | **`FAIL` (INVALID)** | 2023 is not a leap year. |
| **Calendar Math** | Century Non-Leap | `1900-02-29` | **`FAIL` (INVALID)** | 1900 is divisible by 100 but not 400. |
| **Calendar Math** | 30-Day Month Overflow| `2020-04-31` | **`FAIL` (INVALID)** | April has 30 days. |
| **Calendar Math** | Month Bounds | `2020-00-15`, `2020-13-15` | **`FAIL` (INVALID)** | Month must be in $[1, 12]$. |
| **Calendar Math** | Day Bounds | `2020-05-00`, `2020-05-32` | **`FAIL` (INVALID)** | Day must be in $[1, 31]$. |
| **Bearer Names** | International Accents | `JOSÉ MARÍA AZNAR-LÓPEZ` | **`PASS`** | Latin accented characters and hyphens preserved cleanly. |
| **Typography** | Zero-Width & Tabs | `JOHN\u200B SMITH\t\n` | **`PASS`** | Normalizer strips invisible control characters. |
| **Null Data** | Missing Payload Fields| `fields: None` or `{}` | **`UNKNOWN`** | Safe routing to `UNKNOWN`, never crashes. |
| **Adversarial** | SQL/Command Injection | `'; DROP TABLE users; --` | **`INVALID` / `REVIEW_REQUIRED`** | Handled strictly as literal text data without execution. |
