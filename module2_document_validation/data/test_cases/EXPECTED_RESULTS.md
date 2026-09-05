# AI-DIDSS Module 2: Independent Oracle & Expected Results Specification

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**Dataset:** 44 Synthetic Deterministic Test Fixtures  
**Date:** 2026-09-02 (Semantic Correction Revision)  

---

## 1. Overview & Evaluation Contract

This document specifies the exact expected status, failed rules, warnings, and review requirement state for all 44 test cases in `data/test_cases/`. It acts as an independent test oracle, decoupled from runtime code implementation.

---

## 2. Expected Results Matrix

| # | Fixture Name | Doc Type | Expected Overall Status | Key Expected Rule Failures / Triggers | Expected Review Req | Expected Score Range |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| 1 | `valid_passport.json` | `passport` | **`VALID`** | None (All pass) | `false` | $1.0$ |
| 2 | `passport_invalid_number_syntax.json` | `passport` | **`INVALID`** | `FORMAT_PASSPORT_NUMBER_SYNTAX` (Malformed "123") | `true` | $0.60 - 0.80$ |
| 3 | `passport_missing_number.json` | `passport` | **`UNKNOWN`** | `REQ_FIELD_PRESENCE` (Primary ID unavailable) | `true` | $0.50$ |
| 4 | `passport_invalid_dob_calendar.json` | `passport` | **`INVALID`** | `DATE_CALENDAR_VALIDITY` (Feb 30) | `true` | $0.60 - 0.80$ |
| 5 | `expired_passport.json` | `passport` | **`EXPIRED`** | `CHRONO_EXPIRATION_STATUS` (Expired) | `true` | $0.80 - 0.90$ |
| 6 | `passport_issue_after_expiry.json` | `passport` | **`INVALID`** | `CHRONO_ISSUE_BEFORE_EXPIRY` | `true` | $0.60 - 0.80$ |
| 7 | `passport_dob_after_issue.json` | `passport` | **`INVALID`** | `CHRONO_DOB_BEFORE_ISSUE` | `true` | $0.60 - 0.80$ |
| 8 | `mrz_checksum_error.json` | `passport` | **`INVALID`** | `MRZ_DOC_NUMBER_CHECKSUM`, `MRZ_DOB_CHECKSUM`, etc. | `true` | $0.40 - 0.60$ |
| 9 | `visual_mrz_conflict.json` | `passport` | **`REVIEW_REQUIRED`** | `CROSS_VISUAL_MRZ_DOC_NUMBER` | `true` | $0.80 - 0.90$ |
| 10 | `passport_visual_mrz_dob_conflict.json` | `passport` | **`REVIEW_REQUIRED`**| `CROSS_VISUAL_MRZ_DATE_OF_BIRTH` | `true` | $0.80 - 0.90$ |
| 11 | `valid_visa.json` | `visa` | **`VALID`** | None (All pass) | `false` | $1.0$ |
| 12 | `visa_invalid_number.json` | `visa` | **`INVALID`** | `FORMAT_VISA_NUMBER_SYNTAX` (Malformed "V1") | `true` | $0.60 - 0.80$ |
| 13 | `visa_expired.json` | `visa` | **`EXPIRED`** | `CHRONO_EXPIRATION_STATUS` (Expired) | `true` | $0.80 - 0.90$ |
| 14 | `visa_invalid_stay_dates.json` | `visa` | **`INVALID`** | `CHRONO_ISSUE_BEFORE_EXPIRY` | `true` | $0.60 - 0.80$ |
| 15 | `visa_missing_expiry.json` | `visa` | **`UNKNOWN`** | `REQ_FIELD_PRESENCE` (Mandatory expiry unavailable) | `true` | $0.50$ |
| 16 | `visa_low_confidence_m1.json` | `passport` (Mis) | **`REVIEW_REQUIRED`**| `UPSTREAM_REVIEW_FLAG` | `true` | $0.80 - 0.95$ |
| 17 | `visa_mrv_checksum_error.json` | `visa` | **`INVALID`** | `MRZ_DOC_NUMBER_CHECKSUM`, `MRZ_DOB_CHECKSUM` | `true` | $0.50 - 0.70$ |
| 18 | `valid_driver_license.json` | `driver_license` | **`VALID`** | None (All pass) | `false` | $1.0$ |
| 19 | `dl_malformed_number.json` | `driver_license` | **`INVALID`** | `FORMAT_DRIVER_LICENSE_SYNTAX` (Malformed "12") | `true` | $0.60 - 0.80$ |
| 20 | `dl_missing_number.json` | `driver_license` | **`UNKNOWN`** | `REQ_FIELD_PRESENCE` (Primary license unavailable) | `true` | $0.50$ |
| 21 | `dl_underage_driver.json` | `driver_license` | **`INVALID`** | `DOMAIN_DL_MINIMUM_AGE` (< 16 years) | `true` | $0.60 - 0.80$ |
| 22 | `dl_expired.json` | `driver_license` | **`EXPIRED`** | `CHRONO_EXPIRATION_STATUS` (Expired) | `true` | $0.80 - 0.90$ |
| 23 | `dl_unknown_jurisdiction.json` | `driver_license` | **`VALID`** | `JURISDICTION_UNSPECIFIED` (Info/Pass) | `false` | $0.95 - 1.0$ |
| 24 | `dl_impossible_chronology.json` | `driver_license` | **`INVALID`** | `CHRONO_DOB_BEFORE_ISSUE` (Future DOB) | `true` | $0.50 - 0.70$ |
| 25 | `valid_national_id.json` | `national_id` | **`VALID`** | None (All pass) | `false` | $1.0$ |
| 26 | `national_id_malformed_mrz_length.json` | `national_id` | **`INVALID`** | `MRZ_LINE_GEOMETRY` (Truncated Line 1) | `true` | $0.60 - 0.80$ |
| 27 | `national_id_checksum_error.json` | `national_id` | **`INVALID`** | `MRZ_DOC_NUMBER_CHECKSUM` | `true` | $0.50 - 0.70$ |
| 28 | `national_id_visual_mrz_conflict.json` | `national_id` | **`REVIEW_REQUIRED`**| `CROSS_VISUAL_MRZ_DOC_NUMBER` | `true` | $0.80 - 0.90$ |
| 29 | `national_id_missing_id.json` | `national_id` | **`UNKNOWN`** | `REQ_FIELD_PRESENCE` (Primary ID unavailable) | `true` | $0.50$ |
| 30 | `national_id_invalid_dob.json` | `national_id` | **`INVALID`** | `DATE_CALENDAR_VALIDITY` (Month 13) | `true` | $0.60 - 0.80$ |
| 31 | `valid_permit.json` | `permit` | **`VALID`** | None (All pass) | `false` | $1.0$ |
| 32 | `permit_invalid_category.json` | `permit` | **`VALID`** (Warning)| `DOMAIN_PERMIT_CATEGORY_VALIDITY` (Warning) | `false` | $0.85 - 0.95$ |
| 33 | `permit_expired.json` | `permit` | **`EXPIRED`** | `CHRONO_EXPIRATION_STATUS` (Expired) | `true` | $0.80 - 0.90$ |
| 34 | `permit_missing_permit_num.json` | `permit` | **`UNKNOWN`** | `REQ_FIELD_PRESENCE` (Primary permit unavailable) | `true` | $0.50$ |
| 35 | `permit_issue_after_expiry.json` | `permit` | **`INVALID`** | `CHRONO_ISSUE_BEFORE_EXPIRY` | `true` | $0.60 - 0.80$ |
| 36 | `permit_non_standard_category_warning.json` | `permit` | **`VALID`** (Warning)| `DOMAIN_PERMIT_CATEGORY_VALIDITY` (Warning) | `false` | $0.85 - 0.95$ |
| 37 | `malformed_input.json` | `unknown_document`| **`INVALID_INPUT`** | `INPUT_DECODE_FAILURE` | `true` | $0.0$ |
| 38 | `empty_input.json` | `unknown_document`| **`INVALID_INPUT`** | `INPUT_EMPTY_BYTES` | `true` | $0.0$ |
| 39 | `unknown_document.json` | `unknown_document`| **`UNKNOWN`** | `UNIDENTIFIABLE_DOCUMENT` | `true` | $0.50$ |
| 40 | `unsupported_document_type.json` | `voter_card` | **`UNSUPPORTED_DOCUMENT`**| `UNSUPPORTED_DOCUMENT_CLASS` | `true` | $0.50$ |
| 41 | `edge_leap_day_valid.json` | `passport` | **`VALID`** | None (2000-02-29 Leap Day Valid) | `false` | $1.0$ |
| 42 | `edge_leap_day_invalid_nonleap.json`| `passport` | **`INVALID`** | `DATE_CALENDAR_VALIDITY` (2001-02-29 Invalid) | `true` | $0.60 - 0.80$ |
| 43 | `edge_whitespace_resilience.json` | `passport` | **`VALID`** | None (Leading/trailing whitespace stripped) | `false` | $1.0$ |
| 44 | `edge_unicode_name_handling.json` | `passport` | **`VALID`** | None (Unicode accents preserved safely) | `false` | $1.0$ |
