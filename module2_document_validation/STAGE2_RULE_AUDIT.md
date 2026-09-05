# AI-DIDSS Module 2: Stage 2 Validation Rule Audit & Scope Analysis

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Audit Target:** All validation rules implemented in Module 2  
**Date:** 2026-09-02 (Semantic Correction Revision)  

---

## 1. Rule Classification Framework

Every rule in Module 2 is classified under one of three authority tiers:
1. **`AUTHORITATIVE`**: Derived directly from international standards (ICAO Doc 9303, ISO 8601, ISO 3166-1, AAMVA).
2. **`PROJECT_SYNTHETIC_RULE`**: Defined specifically for the synthetic dataset and prototype identity schema.
3. **`HEURISTIC`**: Operational sanity check or heuristic guideline (never to be conflated with government legal requirements).

---

## 2. Updated Granular Rule-by-Rule Audit Matrix

| Rule ID | Category | Authority Tier | Severity | Weight | Target Document Types | Purpose & Technical Scope | Semantic Handling |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| **`REQ_FIELD_PRESENCE`** | `SCHEMA` | `PROJECT_SYNTHETIC_RULE` | `HIGH` | 1.0 | All Supported Types | Checks presence of core identification fields. | **If field is missing/unextracted:** records `UNKNOWN` (propagates uncertainty $\rightarrow$ `UNKNOWN` / `REVIEW_REQUIRED`). **Does NOT trigger `INVALID`.** |
| **`DATE_FORMAT_ISO8601`** | `DATE` | `AUTHORITATIVE` | `MEDIUM` | 0.75 | All Date Fields | Verifies ISO 8601 `YYYY-MM-DD` syntax. | If present and invalid syntax $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`DATE_CALENDAR_VALIDITY`** | `DATE` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | All Date Fields | Verifies physical calendar validity (e.g. leap year Feb 29, month $\in [1, 12]$). | If present and impossible day $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`CHRONO_DOB_BEFORE_ISSUE`** | `CHRONOLOGY` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | All Types with DOB & Issue | Verifies that Date of Birth strictly precedes Document Date of Issue and $\text{DOB} \le \text{Today}$. | If both dates present and chronology violated $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`CHRONO_ISSUE_BEFORE_EXPIRY`**| `CHRONOLOGY`| `AUTHORITATIVE` | `CRITICAL` | 1.0 | All Types with Issue & Expiry | Verifies that Date of Issue strictly precedes Date of Expiry. | If both dates present and issue > expiry $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`CHRONO_EXPIRATION_STATUS`** | `CHRONOLOGY`| `AUTHORITATIVE` | `HIGH` | 0.75 | All Types with Expiry | Checks if expiration date is in the past relative to reference verification date. | If present and in the past $\rightarrow$ `FAIL` (routes to `EXPIRED`). |
| **`MRZ_LINE_GEOMETRY`** | `MRZ` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | Passport, Visa, National ID | Verifies ICAO line lengths (TD1=30, TD2=36, TD3=44, MRV=44). | If MRZ present and lines truncated $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`MRZ_DOC_NUMBER_CHECKSUM`** | `MRZ` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | Passport, Visa, TD1 ID | Recalculates ICAO Modulo-10 7-3-1 check digit for document number. | If MRZ present and check digit wrong $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`MRZ_DOB_CHECKSUM`** | `MRZ` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | Passport, Visa, TD1 ID | Recalculates ICAO Modulo-10 7-3-1 check digit for birth date. | If MRZ present and check digit wrong $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`MRZ_EXPIRY_CHECKSUM`** | `MRZ` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | Passport, Visa, TD1 ID | Recalculates ICAO Modulo-10 7-3-1 check digit for expiry date. | If MRZ present and check digit wrong $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`MRZ_COMPOSITE_CHECKSUM`** | `MRZ` | `AUTHORITATIVE` | `CRITICAL` | 1.0 | Passport, TD1 ID | Recalculates composite master check digit covering core fields. | If MRZ present and check digit wrong $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`CROSS_VISUAL_MRZ_DOC_NUMBER`**| `CONSISTENCY`| `AUTHORITATIVE` | `HIGH` | 1.0 | Passport, Visa, TD1 ID | Verifies character agreement between visual and MRZ document numbers. | If both present and disagree $\rightarrow$ `FAIL` (`HIGH` severity $\rightarrow$ `REVIEW_REQUIRED`). |
| **`CROSS_VISUAL_MRZ_NATIONALITY`**| `CONSISTENCY`| `AUTHORITATIVE` | `HIGH` | 0.75 | Passport, Visa, TD1 ID | Verifies ISO 3166-1 country code equivalence between visual and MRZ. | If both present and disagree $\rightarrow$ `FAIL` (`HIGH` severity $\rightarrow$ `REVIEW_REQUIRED`). |
| **`CROSS_VISUAL_MRZ_EXPIRY`** | `CONSISTENCY`| `AUTHORITATIVE` | `HIGH` | 1.0 | Passport, Visa, TD1 ID | Verifies expiration date equivalence between visual and MRZ zones. | If both present and disagree $\rightarrow$ `FAIL` (`HIGH` severity $\rightarrow$ `REVIEW_REQUIRED`). |
| **`FORMAT_COUNTRY_ISO3`** | `FORMAT` | `AUTHORITATIVE` | `MEDIUM` | 0.50 | All Country Fields | Checks country against ISO 3166-1 alpha-3 code list. | If present and not in dictionary $\rightarrow$ `WARNING`. |
| **`FORMAT_PASSPORT_NUMBER_SYNTAX`**| `FORMAT`| `PROJECT_SYNTHETIC_RULE`| `CRITICAL`| 1.0 | Passport | Alphanumeric booklet number length (6 to 12 chars). | If present and violates syntax $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`FORMAT_VISA_NUMBER_SYNTAX`**| `FORMAT`| `PROJECT_SYNTHETIC_RULE`| `CRITICAL`| 1.0 | Visa | Alphanumeric visa number syntax. | If present and violates syntax $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`FORMAT_DRIVER_LICENSE_SYNTAX`** | `FORMAT` | `PROJECT_SYNTHETIC_RULE`| `CRITICAL`| 1.0 | Driver's License | Alphanumeric license number format. | If present and violates syntax $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`FORMAT_NATIONAL_ID_SYNTAX`** | `FORMAT` | `PROJECT_SYNTHETIC_RULE`| `CRITICAL`| 1.0 | National ID | Alphanumeric national ID syntax. | If present and violates syntax $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`FORMAT_PERMIT_NUMBER_SYNTAX`** | `FORMAT` | `PROJECT_SYNTHETIC_RULE`| `CRITICAL`| 1.0 | Permit | Alphanumeric permit number syntax. | If present and violates syntax $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`DOMAIN_PASSPORT_VALIDITY_SPAN`**| `DOMAIN` | `HEURISTIC` | `MEDIUM` | 0.50 | Passport | Verifies validity duration does not exceed 10.5 years. | If exceeded $\rightarrow$ `WARNING`. |
| **`DOMAIN_DL_MINIMUM_AGE`** | `DOMAIN` | `HEURISTIC` | `CRITICAL` | 1.0 | Driver's License | Verifies driver age is $\ge 16$ years at license issuance. | If age < 16 years $\rightarrow$ `FAIL` (`CRITICAL` severity $\rightarrow$ `INVALID`). |
| **`DOMAIN_PERMIT_CATEGORY_VALIDITY`**| `DOMAIN`| `PROJECT_SYNTHETIC_RULE`| `LOW`| 0.50 | Residence Permit | Checks permit category against authorized immigration list. | If non-standard category $\rightarrow$ `WARNING`. |

---

## 3. Clear Distinction: Importance vs Invalidation

* **Severity `CRITICAL`** on format rules, dates, and checksums means that when the data is extracted and demonstrably impossible/corrupted, it **invalidates** the optical document structure (`INVALID`).
* **Missing Data (`REQ_FIELD_PRESENCE`)** means the evidence is unavailable or uncertain, which maps to **`UNKNOWN`** or **`REVIEW_REQUIRED`** to prevent punishing OCR extraction failures as physical document invalidity.
